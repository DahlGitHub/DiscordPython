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

    # === Steam connection ===

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

    # === Wishlist users ===

    @app_commands.command(name="add", description="Register a public Steam wishlist")
    @app_commands.describe(
        profile="Steam profile URL or SteamID64", member="Leave empty to register yourself"
    )
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    async def add_user(
        self, interaction: discord.Interaction, profile: str, member: discord.Member = None
    ):
        """Register a public Steam wishlist using a profile URL or SteamID64."""
        await interaction.response.defer()
        member = member or interaction.user
        if member.id != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            raise app_commands.MissingPermissions(["manage_guild"])
        if member.bot:
            await interaction.followup.send("Choose a human member.")
            return
        async with self.tracker.lock:
            client = self.client()
            steam_id = await client.resolve(profile)
            # Verify accessibility before replacing an existing registration.
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
        )

    @app_commands.command(name="remove", description="Remove a Steam wishlist registration")
    async def remove_user(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()
        member = member or interaction.user
        if member.id != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            raise app_commands.MissingPermissions(["manage_guild"])
        async with self.tracker.lock:
            await self.bot.sqlite.execute(
                "DELETE FROM steam_users WHERE guild_id = ? AND user_id = ?",
                interaction.guild.id,
                member.id,
            )
        await interaction.followup.send("Wishlist registration removed.")

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

    # === View wishlist ===

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

    # === Alert settings ===

    @app_commands.command(name="setchannel", description="Choose the Steam alert channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()
        if channel.guild.id != interaction.guild.id:
            await interaction.followup.send("Choose a channel in this server.")
            return
        permissions = channel.permissions_for(interaction.guild.me)
        if not (permissions.view_channel and permissions.send_messages and permissions.embed_links):
            await interaction.followup.send(
                "I need View Channel, Send Messages, and Embed Links there."
            )
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
        )

    @app_commands.command(name="disable", description="Disable automatic Steam alerts")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def disable(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with self.tracker.lock:
            await self.bot.sqlite.execute(
                "DELETE FROM steam_channels WHERE guild_id = ?", interaction.guild.id
            )
        await interaction.followup.send("Steam alerts disabled. Registered users are preserved.")

    @app_commands.command(name="check", description="Check wishlists for sales and releases now")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 60, key=lambda i: i.guild_id)
    async def check(self, interaction: discord.Interaction):
        await interaction.response.defer()
        posted, skipped = await self.tracker.check_all(interaction.guild.id)
        await interaction.followup.send(
            f"Check complete: {posted} game alerts posted; {skipped} checks skipped or failed. "
            "Alerts require a configured channel and registered users."
        )

    # === Command errors ===

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        interaction.extras["command_error_handled"] = True
        original = getattr(error, "original", error)
        if isinstance(original, SteamError):
            message = str(original)
        elif isinstance(original, (aiohttp.ClientError, asyncio.TimeoutError)):
            message = "Steam is unavailable or rate-limiting requests. Try again later."
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
