from __future__ import annotations

import asyncio
import json
from datetime import date, datetime, timezone
from pathlib import Path

import discord
from discord.ext import commands, tasks

from utils.scrapelol import (
    LeaguePatch,
    PatchFetchError,
    get_latest_patch,
    get_latest_patch_url,
)


STATE_FILE = Path(
    "data/league_patches.json"
)


PATCH_REFERENCE_DATE = date(
    2026,
    7,
    15,
)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {
            "channel_id": None,
            "last_patch_url": None,
        }

    try:
        with STATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {
            "channel_id": None,
            "last_patch_url": None,
        }

    return {
        "channel_id": data.get(
            "channel_id"
        ),
        "last_patch_url": data.get(
            "last_patch_url"
        ),
    }


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with STATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            indent=4,
        )


def is_patch_window(
    current_date: date,
) -> bool:
    """
    Return True on the expected patch Wednesday
    and the following Thursday.

    No Riot request is made outside this window.
    """

    days_since_reference = (
        current_date
        - PATCH_REFERENCE_DATE
    ).days

    if days_since_reference < 0:
        return False

    cycle_day = (
        days_since_reference % 14
    )

    return cycle_day in (
        0,
        1,
    )


def create_patch_embed(
    patch: LeaguePatch,
) -> discord.Embed:

    description = (
        patch.description
        or "No patch description found."
    )

    if len(description) > 4000:
        description = (
            description[:2000]
            .rsplit(
                " ",
                1,
            )[0]
            + "..."
        )

    embed = discord.Embed(
        title=patch.title,
        url=patch.url,
        description=description,
        color=discord.Color.red(),
    )

    embed.set_author(
        name="League of Legends",
    )

    if patch.image_url:
        embed.set_image(
            url=patch.image_url,
        )

    embed.set_footer(
        text=patch.title,
    )

    return embed


class Patches(
    commands.Cog,
    name="Patches",
):
    def __init__(
        self,
        bot: commands.Bot,
    ):
        self.bot = bot

        self.patch_checker.start()

    def cog_unload(self):
        self.patch_checker.cancel()

    # -----------------------------------
    # PATCHES COMMAND GROUP
    # -----------------------------------

    @commands.group(
        name="patches",
        invoke_without_command=True,
    )
    async def patches(
        self,
        ctx: commands.Context,
    ):
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

    @patches.command(
        name="test",
    )
    async def patches_test(
        self,
        ctx: commands.Context,
    ):
        """
        Fetch and display the newest patch.

        This ignores saved state and always fetches
        the newest Riot patch for testing.
        """

        async with ctx.typing():
            try:
                patch = await asyncio.to_thread(
                    get_latest_patch
                )

            except PatchFetchError as exc:
                await ctx.send(
                    "❌ Failed to fetch "
                    f"League patch:\n`{exc}`"
                )
                return

        embed = create_patch_embed(
            patch
        )

        await ctx.send(
            embed=embed
        )

    # -----------------------------------
    # SET CHANNEL
    # -----------------------------------

    @patches.command(
        name="setchannel",
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def patches_set_channel(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel
        | None = None,
    ):
        """
        Set the channel where new patches
        should automatically be posted.

        Usage:
        patches setchannel
        patches setchannel #patch-notes
        """

        channel = (
            channel
            or ctx.channel
        )

        if not isinstance(
            channel,
            discord.TextChannel,
        ):
            await ctx.send(
                "❌ This must be a text channel."
            )
            return

        state = load_state()

        state["channel_id"] = (
            channel.id
        )

        save_state(
            state
        )

        await ctx.send(
            "✅ League patch updates "
            f"will be posted in {channel.mention}."
        )

    # -----------------------------------
    # SHOW CHANNEL
    # -----------------------------------

    @patches.command(
        name="channel",
    )
    async def patches_channel(
        self,
        ctx: commands.Context,
    ):
        state = load_state()

        channel_id = state.get(
            "channel_id"
        )

        if not channel_id:
            await ctx.send(
                "No League patch channel "
                "has been configured."
            )
            return

        channel = self.bot.get_channel(
            channel_id
        )

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

    @tasks.loop(
        hours=2,
    )
    async def patch_checker(
        self,
    ):
        """
        Wake every 2 hours.

        Outside the expected biweekly Wednesday /
        Thursday patch window, immediately return.

        This means almost all task runs make
        ZERO HTTP requests to Riot.
        """

        today = datetime.now(
            timezone.utc
        ).date()

        if not is_patch_window(
            today
        ):
            return

        state = load_state()

        channel_id = state.get(
            "channel_id"
        )

        # Nothing to do until a channel is configured.
        if not channel_id:
            return

        channel = self.bot.get_channel(
            channel_id
        )

        if not isinstance(
            channel,
            discord.TextChannel,
        ):
            return

        try:
            latest_url = await asyncio.to_thread(
                get_latest_patch_url
            )

        except PatchFetchError:
            return

        previous_url = state.get(
            "last_patch_url"
        )

        # First run:
        #
        # Remember whatever patch currently exists,
        # but don't suddenly announce an old patch.
        if previous_url is None:
            state[
                "last_patch_url"
            ] = latest_url

            save_state(
                state
            )

            return

        # Nothing new.
        if latest_url == previous_url:
            return

        # Only fetch the full article once the URL changed.
        try:
            patch = await asyncio.to_thread(
                get_latest_patch
            )

        except PatchFetchError:
            return

        embed = create_patch_embed(
            patch
        )

        try:
            await channel.send(
                embed=embed
            )

        except discord.HTTPException:
            # Do NOT update state if Discord failed,
            # otherwise the patch would be lost.
            return

        # Only save after a successful Discord post.
        state[
            "last_patch_url"
        ] = patch.url

        save_state(
            state
        )

    @patch_checker.before_loop
    async def before_patch_checker(
        self,
    ):
        await self.bot.wait_until_ready()


async def setup(
    bot: commands.Bot,
):
    await bot.add_cog(
        Patches(bot)
    )