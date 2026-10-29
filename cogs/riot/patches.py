from __future__ import annotations

import asyncio
import json
from pathlib import Path

import discord
from discord.ext import commands, tasks

from utils.scrapelol import (
    LeaguePatch,
    PatchFetchError,
    get_latest_patch,
    get_latest_patch_url,
)


STATE_FILE = Path("data/league_patches.json")


def load_legacy_state() -> dict:
    try:
        with STATE_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        data = {}

    return {
        "channel_id": data.get("channel_id"),
        "last_patch_url": data.get("last_patch_url"),
    }


async def load_state(db, old_db=None) -> dict:
    row = await db.fetchrow("SELECT channel_id, last_patch_url FROM league_patches WHERE id = 1")
    if row is None:
        # Import the old file once; subsequent reads use the database only.
        state = None
        # Preserve state from the short-lived PostgreSQL version, if present.
        if old_db is not None and old_db.pool is not None:
            exists = await old_db.fetchval("SELECT to_regclass('public.league_patches')")
            if exists:
                state = await old_db.fetchrow(
                    "SELECT channel_id, last_patch_url FROM league_patches WHERE id = 1"
                )
        if state is None:
            state = load_legacy_state()
        await db.execute(
            "INSERT INTO league_patches (id, channel_id, last_patch_url) "
            "VALUES (1, ?, ?) ON CONFLICT (id) DO NOTHING",
            state["channel_id"],
            state["last_patch_url"],
        )
        row = await db.fetchrow("SELECT channel_id, last_patch_url FROM league_patches WHERE id = 1")
    return dict(row)


async def save_patch_url(db, url: str) -> None:
    await db.execute(
        "UPDATE league_patches SET last_patch_url = ? WHERE id = 1",
        url,
    )


def create_patch_embed(patch: LeaguePatch) -> discord.Embed:

    description = patch.description or "No patch description found."

    if len(description) > 4000:
        description = description[:2000].rsplit(" ", 1)[0] + "..."

    embed = discord.Embed(
        title=patch.title,
        url=patch.url,
        description=description,
        color=discord.Color.red(),
    )

    embed.set_author(name="League of Legends")

    if patch.image_url:
        embed.set_image(url=patch.image_url)

    embed.set_footer(text=patch.title)

    return embed


class Patches(commands.Cog, name="Patches"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.patch_checker.start()

    def cog_unload(self):
        self.patch_checker.cancel()

    # -----------------------------------
    # PATCHES COMMAND GROUP
    # -----------------------------------

    @commands.group(name="patches", invoke_without_command=True)
    async def patches(self, ctx: commands.Context):
        """
        League patch-note commands.
        """

        await ctx.send(
            "Available commands:\n"
            "`patches test`\n"
            "`patches setchannel`\n"
            "`patches channel`"
        )

    # -----------------------------------
    # TEST
    # -----------------------------------

    @patches.command(name="test")
    async def patches_test(self, ctx: commands.Context):
        """
        Fetch and display the newest patch.

        This ignores saved state and always fetches
        the newest Riot patch for testing.
        """

        async with ctx.typing():
            try:
                patch = await asyncio.to_thread(get_latest_patch)

            except PatchFetchError as exc:
                await ctx.send(
                    "❌ Failed to fetch "
                    f"League patch:\n`{exc}`"
                )
                return

        embed = create_patch_embed(patch)

        await ctx.send(embed=embed)

    # -----------------------------------
    # SET CHANNEL
    # -----------------------------------

    @patches.command(name="setchannel")
    @commands.has_permissions(manage_guild=True)
    async def patches_set_channel(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel | None = None,
    ):
        """
        Set the channel where new patches
        should automatically be posted.

        Usage:
        patches setchannel
        patches setchannel #patch-notes
        """

        channel = channel or ctx.channel

        if not isinstance(channel, discord.TextChannel):
            await ctx.send("❌ This must be a text channel.")
            return

        await load_state(self.bot.sqlite, self.bot.db)
        await self.bot.sqlite.execute(
            "UPDATE league_patches SET channel_id = ? WHERE id = 1",
            channel.id,
        )

        await ctx.send(
            "✅ League patch updates "
            f"will be posted in {channel.mention}."
        )

    # -----------------------------------
    # SHOW CHANNEL
    # -----------------------------------

    @patches.command(name="channel")
    async def patches_channel(self, ctx: commands.Context):
        state = await load_state(self.bot.sqlite, self.bot.db)

        channel_id = state.get("channel_id")

        if not channel_id:
            await ctx.send(
                "No League patch channel "
                "has been configured."
            )
            return

        channel = self.bot.get_channel(channel_id)

        if channel is None:
            await ctx.send(
                "The saved patch channel "
                "no longer exists."
            )
            return

        await ctx.send(
            "League patch updates are "
            f"configured for {channel.mention}."
        )

    # -----------------------------------
    # AUTOMATIC CHECKER
    # -----------------------------------

    @tasks.loop(hours=24)
    async def patch_checker(self):
        """
        Check for new patch notes every 24 hours.
        """

        state = await load_state(self.bot.sqlite, self.bot.db)

        channel_id = state.get("channel_id")

        # Nothing to do until a channel is configured.
        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)

        if not isinstance(channel, discord.TextChannel):
            return

        try:
            latest_url = await asyncio.to_thread(get_latest_patch_url)

        except PatchFetchError:
            return

        previous_url = state.get("last_patch_url")

        # First run:
        #
        # Remember whatever patch currently exists,
        # but don't suddenly announce an old patch.
        if previous_url is None:
            await save_patch_url(self.bot.sqlite, latest_url)

            return

        # Nothing new.
        if latest_url == previous_url:
            return

        # Only fetch the full article once the URL changed.
        try:
            patch = await asyncio.to_thread(get_latest_patch)

        except PatchFetchError:
            return

        embed = create_patch_embed(patch)

        try:
            await channel.send(embed=embed)

        except discord.HTTPException:
            # Do NOT update state if Discord failed,
            # otherwise the patch would be lost.
            return

        # Only save after a successful Discord post.
        await save_patch_url(self.bot.sqlite, patch.url)

    @patch_checker.before_loop
    async def before_patch_checker(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Patches(bot))
