"""Daily shared Steam wishlist sale and release alerts."""

import asyncio
import io
import json
import logging

import aiohttp
import discord
from discord.ext import commands, tasks

import config
from utils.steam import SteamClient, SteamError, changes, game_state
from utils.steamviews import notification

log = logging.getLogger(__name__)


class SteamNotifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()

    async def cog_load(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        self.watcher.start()

    async def cog_unload(self):
        self.watcher.cancel()
        await self.session.close()

    def client(self):
        return SteamClient(self.session, config.STEAM_API_KEY, config.STEAM_COUNTRY)

    # === Check registered wishlists ===

    async def check_all(self, guild_id=None):
        posted = skipped = 0
        async with self.lock:
            channels = await self.bot.sqlite.fetch(
                "SELECT guild_id, channel_id FROM steam_channels"
            )
            client = self.client()  # Shares details across users and servers for this check only.
            for target in channels:
                if guild_id is not None and guild_id != target["guild_id"]:
                    continue
                channel = self.bot.get_channel(target["channel_id"])
                if not isinstance(channel, discord.TextChannel):
                    skipped += 1
                    continue
                try:
                    count = await self.check_guild(client, channel)
                    posted += count
                except (
                    SteamError,
                    aiohttp.ClientError,
                    asyncio.TimeoutError,
                    discord.HTTPException,
                ):
                    # Avoid logging exception URLs: vanity requests may contain an API key.
                    log.warning(
                        "Steam wishlist check failed for guild %s; retrying next day",
                        target["guild_id"],
                    )
                    skipped += 1
        return posted, skipped

    async def check_guild(self, client, channel):
        guild_id = channel.guild.id
        users = await self.bot.sqlite.fetch(
            """
            SELECT user_id, steam_id, wishlist
            FROM steam_users
            WHERE guild_id = ?
            """,
            guild_id,
        )
        current_users = {}
        previous_users = {}
        refreshed = []
        for user in users:
            # A failed wishlist aborts this server's check rather than posting an incomplete subscriber list.
            app_ids = await client.wishlist(user["steam_id"])
            refreshed.append((user["user_id"], app_ids))
            for app_id in app_ids:
                current_users.setdefault(app_id, set()).add(user["user_id"])
            for app_id in json.loads(user["wishlist"]):
                previous_users.setdefault(app_id, set()).add(user["user_id"])
        rows = await self.bot.sqlite.fetch(
            "SELECT app_id, state FROM steam_games WHERE guild_id = ?", guild_id
        )
        states = {row["app_id"]: json.loads(row["state"]) for row in rows}
        # Retain just-removed coming-soon entries for this check: buying on release may remove a wishlist item.
        candidates = set(current_users)
        for app_id in previous_users:
            if states.get(app_id, {}).get("coming_soon") is True:
                candidates.add(app_id)
        posted = 0
        incomplete = False
        for app_id in sorted(candidates):
            try:
                game = await client.details(app_id)
            except SteamError:
                # Delisted/region-locked apps should not block every other game.
                # Keep prior wishlists to retry any just-removed releases next time.
                incomplete = True
                continue
            state = game_state(game, config.STEAM_COUNTRY)
            previous = states.get(app_id)
            # Missing prices should not erase the last known sale.
            if previous and previous["country"] == state["country"] and state["price"] is None:
                for field in ("price", "currency", "discount"):
                    state[field] = previous[field]
            events = changes(previous, state)
            subscribers = current_users.get(app_id, set())
            if "Now available" in events:
                subscribers = subscribers | previous_users.get(app_id, set())
            if app_id not in current_users:
                events = [event for event in events if event == "Now available"]
            if events and subscribers:
                embed = notification(game, events, subscribers)
                kwargs = {"embed": embed, "allowed_mentions": discord.AllowedMentions.none()}
                if any("attached list" in field.value for field in embed.fields):
                    kwargs["file"] = discord.File(
                        io.BytesIO("\n".join(str(uid) for uid in sorted(subscribers)).encode()),
                        filename="wishlist-users.txt",
                    )
                await channel.send(**kwargs)
                posted += 1
            # Only acknowledge events after Discord accepts the message.
            await self.bot.sqlite.execute(
                """
                INSERT INTO steam_games VALUES (?, ?, ?) ON CONFLICT(guild_id, app_id)
                DO UPDATE SET state = excluded.state
                """,
                guild_id,
                app_id,
                json.dumps(state),
            )
        if not incomplete:
            for user_id, app_ids in refreshed:
                await self.bot.sqlite.execute(
                    """
                    UPDATE steam_users SET wishlist = ?
                    WHERE guild_id = ? AND user_id = ?
                    """,
                    json.dumps(app_ids),
                    guild_id,
                    user_id,
                )
        return posted

    # === Daily checker ===

    @tasks.loop(hours=24)
    async def watcher(self):
        try:
            await self.check_all()
        except Exception:
            log.error("Unexpected Steam watcher failure; retrying next day")

    @watcher.before_loop
    async def before_watcher(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(SteamNotifications(bot))
