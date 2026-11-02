"""Commands to register Steam users, browse wishlists, and configure alerts."""

import asyncio
import json
import logging

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

import config
from utils.paginator import ButtonPaginator
from utils.steam import SteamClient, SteamError
from utils.steamviews import WishlistPaginator

log = logging.getLogger(__name__)


@app_commands.guild_only()
class Steam(
    commands.GroupCog,
    group_name="steam",
    group_description="Steam wishlists and sale/release alerts",
):
    def __init__(self, bot):
        self.bot = bot


    @property
    def tracker(self):
        tracker = self.bot.get_cog("SteamNotifications")
        if tracker is None:
            raise SteamError("Load cogs.steam.notifications to enable Steam tracking.")
        return tracker

    async def cog_load(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))

    async def cog_unload(self):
        await self.session.close()

    def client(self):
        return SteamClient(self.session, config.STEAM_API_KEY, config.STEAM_COUNTRY)


    @app_commands.command(name="add", description="Register a public Steam wishlist")
    @app_commands.describe(
        profile="Steam profile URL or SteamID64", member="Leave empty to register yourself"
    )
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    async def add_user(
        self, interaction: discord.Interaction, profile: str, member: discord.Member = None
    ):
        """Register a public Steam wishlist using a profile URL or SteamID64."""
        await interaction.response.defer(ephemeral=True)
        member = member or interaction.user
        if member.id != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            raise app_commands.MissingPermissions(["manage_guild"])
        if member.bot:
            await interaction.followup.send("Choose a human member.", ephemeral=True)
            return
        async with self.tracker.lock:
            client = self.client()
            steam_id = await client.resolve(profile)
            wishlist = await client.wishlist(steam_id)
            await self.bot.sqlite.execute(
                """
                INSERT INTO steam_users (guild_id, user_id, steam_id, wishlist) VALUES (?, ?, ?, ?) ON CONFLICT(guild_id, user_id)
                DO UPDATE SET steam_id = excluded.steam_id, wishlist = excluded.wishlist
                """,
                interaction.guild.id,
                member.id,
                steam_id,
                json.dumps(wishlist),
            )
        await interaction.followup.send(
            f"Registered {member.mention}: {len(wishlist)} wishlist games. Alerts require `/steam setchannel`.",
            allowed_mentions=discord.AllowedMentions.none(),
         ephemeral=True)

    @app_commands.command(name="remove", description="Remove a Steam wishlist registration")
    async def remove_user(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        member = member or interaction.user
        if member.id != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            raise app_commands.MissingPermissions(["manage_guild"])
        async with self.tracker.lock:
            await self.bot.sqlite.execute(
                "DELETE FROM steam_users WHERE guild_id = ? AND user_id = ?",
                interaction.guild.id,
                member.id,
            )
        await interaction.followup.send("Wishlist registration removed.", ephemeral=True)

    @app_commands.command(name="users", description="List registered Steam users")
    async def users(self, interaction: discord.Interaction):
        await interaction.response.defer()
        rows = await self.bot.sqlite.fetch(
            "SELECT user_id, steam_id FROM steam_users WHERE guild_id = ?", interaction.guild.id
        )
        if not rows:
            await interaction.followup.send("No Steam users registered yet.")
            return
        lines = [
            f"<@{row['user_id']}> — [Steam profile](https://steamcommunity.com/profiles/{row['steam_id']}/)"
            for row in rows
        ]
        pages = [
            discord.Embed(
                title="Registered Steam users",
                description="\n".join(lines[i : i + 10]),
                color=config.Color_Default,
            )
            for i in range(0, len(lines), 10)
        ]
        await ButtonPaginator(pages, author_id=interaction.user.id).start(
            interaction, allowed_mentions=discord.AllowedMentions.none()
        )


    @app_commands.command(
        name="wishlist", description="Browse a registered member's Steam wishlist"
    )
    @app_commands.describe(member="Leave empty to view your own wishlist")
    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id, i.user.id))
    async def wishlist(self, interaction: discord.Interaction, member: discord.Member = None):
        """View a registered member's live public wishlist."""
        await interaction.response.defer()
        member = member or interaction.user
        row = await self.bot.sqlite.fetchrow(
            "SELECT steam_id FROM steam_users WHERE guild_id = ? AND user_id = ?",
            interaction.guild.id,
            member.id,
        )
        if row is None:
            await interaction.followup.send(
                "That member has no registered Steam profile. Use `/steam add <profile>`."
            )
            return
        client = self.client()
        app_ids = await client.wishlist(row["steam_id"])
        if not app_ids:
            await interaction.followup.send("Steam returned an empty wishlist.")
            return
        paginator = WishlistPaginator(app_ids, member, row["steam_id"], client)
        paginator.author_id = interaction.user.id
        await paginator.start(interaction, allowed_mentions=discord.AllowedMentions.none())


    @app_commands.command(name="status", description="Show Steam settings and scheduled checks")
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel = await self.bot.sqlite.fetchrow(
            "SELECT channel_id FROM steam_channels WHERE guild_id = ?", interaction.guild.id
        )
        users = await self.bot.sqlite.fetch(
            "SELECT user_id FROM steam_users WHERE guild_id = ?", interaction.guild.id
        )
        promos = await self.bot.sqlite.fetch(
            "SELECT kind, channel_id FROM steam_promo_channels WHERE guild_id = ?", interaction.guild.id
        )
        embed = discord.Embed(title="Steam status", color=config.Color_Default)
        embed.add_field(name="Users", value=str(len(users)))
        embed.add_field(name="Wishlist alerts", value=f"<#{channel['channel_id']}>" if channel else "Disabled")
        for kind, name in (("freegames", "Free games"), ("freeweekends", "Free weekends")):
            target = next((row for row in promos if row["kind"] == kind), None)
            embed.add_field(name=name, value=f"<#{target['channel_id']}>" if target else "Disabled")
        for cog_name, loop_name, name in (
            ("SteamNotifications", "watcher", "Wishlists"),
            ("SteamPromotions", "free_checker", "Free games"),
            ("SteamPromotions", "weekend_checker", "Weekend schedule"),
        ):
            cog = self.bot.get_cog(cog_name)
            if cog is None:
                value = "Cog not loaded"
            else:
                loop = getattr(cog, loop_name)
                when = loop.next_iteration
                value = f"Next run: {discord.utils.format_dt(when, 'R')}" if loop.is_running() and when else "Not scheduled"
                if loop_name == "weekend_checker":
                    value += "\nOffers checked Thursday at 18:00 Europe/Oslo."
            embed.add_field(name=name, value=value, inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="setchannel", description="Choose the Steam alert channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        if channel.guild.id != interaction.guild.id:
            await interaction.followup.send("Choose a channel in this server.", ephemeral=True)
            return
        permissions = channel.permissions_for(interaction.guild.me)
        if not (permissions.view_channel and permissions.send_messages and permissions.embed_links):
            await interaction.followup.send(
                "I need View Channel, Send Messages, and Embed Links there."
            , ephemeral=True)
            return
        async with self.tracker.lock:
            await self.bot.sqlite.execute(
                """
                INSERT INTO steam_channels VALUES (?, ?) ON CONFLICT(guild_id)
                DO UPDATE SET channel_id = excluded.channel_id
                """,
                interaction.guild.id,
                channel.id,
            )
        await interaction.followup.send(
            f"Daily Steam wishlist alerts enabled in {channel.mention}. Use `/steam check` to check now."
        , ephemeral=True)

    @app_commands.command(name="disable", description="Disable automatic Steam alerts")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def disable(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        async with self.tracker.lock:
            await self.bot.sqlite.execute(
                "DELETE FROM steam_channels WHERE guild_id = ?", interaction.guild.id
            )
        await interaction.followup.send("Steam alerts disabled. Registered users are preserved.", ephemeral=True)

    @app_commands.command(name="check", description="Check wishlists for sales and releases now")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 60, key=lambda i: i.guild_id)
    async def check(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel = await self.bot.sqlite.fetchrow(
            "SELECT channel_id FROM steam_channels WHERE guild_id = ?", interaction.guild.id
        )
        if channel is None:
            await interaction.followup.send("No wishlist alert channel configured. Use `/steam setchannel`.", ephemeral=True)
            return
        users = await self.bot.sqlite.fetch(
            "SELECT user_id FROM steam_users WHERE guild_id = ?", interaction.guild.id
        )
        if not users:
            await interaction.followup.send("No registered users. Use `/steam add` first.", ephemeral=True)
            return
        posted, skipped = await self.tracker.check_all(interaction.guild.id)
        await interaction.followup.send(
            f"Check complete: {posted} new game alerts posted in <#{channel['channel_id']}>. "
            + ("Some checks failed or were skipped; results may be incomplete." if skipped else "Previously reported events are skipped.")
        , ephemeral=True)


    @app_commands.command(name='promochannel', description='Configure automatic Steam promotion posts')
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.choices(kind=[
        app_commands.Choice(name='Free games (every 12 hours)', value='freegames'),
        app_commands.Choice(name='Free weekends (Thursday 18:00 Norway)', value='freeweekends'),
    ])
    async def promochannel(self, interaction: discord.Interaction, kind: str, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        if kind not in ('freegames', 'freeweekends'):
            raise SteamError('Choose free games or free weekends.')
        if self.bot.get_cog('SteamPromotions') is None:
            raise SteamError('Load cogs.steam.promotions to enable promotion checks.')
        permissions = channel.permissions_for(interaction.guild.me)
        if channel.guild.id != interaction.guild.id or not (
            permissions.view_channel and permissions.send_messages and permissions.embed_links
        ):
            raise SteamError('Choose a channel in this server where I can view, send messages, and embed links.')
        await self.bot.sqlite.execute(
            'INSERT INTO steam_promo_channels VALUES (?, ?, ?) ON CONFLICT(guild_id, kind) DO UPDATE SET channel_id = excluded.channel_id',
            interaction.guild.id, kind, channel.id,
        )
        await interaction.followup.send(f'{kind} posts enabled in {channel.mention}. Use `/steam promocheck` to check now.', ephemeral=True)

    @app_commands.command(name='promodisable', description='Disable one type of automatic Steam promotion posts')
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.choices(kind=[
        app_commands.Choice(name='Free games', value='freegames'),
        app_commands.Choice(name='Free weekends', value='freeweekends'),
    ])
    async def promodisable(self, interaction: discord.Interaction, kind: str):
        await interaction.response.defer(ephemeral=True)
        await self.bot.sqlite.execute(
            'DELETE FROM steam_promo_channels WHERE guild_id = ? AND kind = ?', interaction.guild.id, kind
        )
        await interaction.followup.send(f'Automatic {kind} posts disabled.', ephemeral=True)

    async def show_promotions(self, interaction, kinds):
        await interaction.response.defer(ephemeral=True)
        tracker = self.bot.get_cog('SteamPromotions')
        if tracker is None:
            raise SteamError('Load cogs.steam.promotions to enable promotion checks.')
        lines = []
        for kind in kinds:
            label = 'Free games' if kind == 'freegames' else 'Free weekends'
            channel = await self.bot.sqlite.fetchrow(
                'SELECT channel_id FROM steam_promo_channels WHERE guild_id = ? AND kind = ?',
                interaction.guild.id, kind,
            )
            if channel is None:
                lines.append(f'{label}: disabled. Choose a destination using `/steam promochannel`.')
                continue
            try:
                posted, failed = await tracker.check(kind, interaction.guild.id)
            except (SteamError, aiohttp.ClientError, asyncio.TimeoutError) as exc:
                log.warning('Manual Steam %s check failed (%s)', kind, type(exc).__name__)
                lines.append(f'{label}: Steam lookup failed; try again later.')
                continue
            lines.append(
                f"{label}: {posted} new offers posted in <#{channel['channel_id']}>. "
                + ('Delivery failed; check channel access and permissions.' if failed else
                   'No new unposted offers found.' if not posted else 'Previously posted offers are skipped.')
            )
        lines.append('Discovery samples up to 100 sale and 100 free search results; some offers may be missed.')
        await interaction.followup.send('\n'.join(lines), ephemeral=True)

    @app_commands.command(name='promocheck', description='Check free games and free weekends now')
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 60, key=lambda i: i.guild_id)
    async def promocheck(self, interaction: discord.Interaction):
        await self.show_promotions(interaction, ('freegames', 'freeweekends'))

    @app_commands.command(name='freeweekends', description='Check free weekends now and post new offers to the configured channel')
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 60, key=lambda i: i.guild_id)
    async def freeweekends(self, interaction: discord.Interaction):
        await self.show_promotions(interaction, ('freeweekends',))

    @app_commands.command(name='freegames', description='Check free-to-keep games now and post new offers to the configured channel')
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 60, key=lambda i: i.guild_id)
    async def freegames(self, interaction: discord.Interaction):
        await self.show_promotions(interaction, ('freegames',))


    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        interaction.extras["command_error_handled"] = True
        original = getattr(error, "original", error)
        if isinstance(original, SteamError):
            message = str(original)
        elif isinstance(original, (aiohttp.ClientError, asyncio.TimeoutError)):
            message = "Steam is unavailable or rate-limiting requests. Try again later."
        elif isinstance(original, discord.HTTPException):
            message = (f"Discord rejected the Steam response (HTTP {original.status}, "
                       f"code {original.code}). {original.text}")[:1800]
            log.error("Steam Discord response failed (HTTP %s, code %s): %s",
                      original.status, original.code, original.text)
        elif isinstance(error, app_commands.MissingPermissions):
            message = "You need Manage Server to manage other members or alerts."
        elif isinstance(error, app_commands.CommandOnCooldown):
            message = f"Try again in {error.retry_after:.0f} seconds."
        else:
            message = "Steam command failed. Please try again later."
            log.error("Steam command failed (%s)", type(original).__name__)
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Steam(bot))
