import asyncio
import re
from pathlib import Path

import discord
from discord.ext import commands


BOT_DIR = Path("/home/pi/DiscordPython")
VENV_PYTHON = BOT_DIR / "venv" / "bin" / "python"


class PipInstaller(commands.Cog):
    """
    Owner-only package management for the bot venv.
    """

    def __init__(self, bot):
        self.bot = bot

    async def run_command(self, *args):
        """
        Run a command inside the bot directory.

        Returns:
            return_code, output
        """

        process = await asyncio.create_subprocess_exec(
            *args,
            cwd=BOT_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        try:
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=300
            )

        except asyncio.TimeoutError:
            process.kill()

            return (
                1,
                "Command timed out after 5 minutes."
            )

        output = stdout.decode(
            errors="replace"
        ).strip()

        return process.returncode, output

    @commands.command(
        name="install",
        hidden=True
    )
    @commands.is_owner()
    @commands.cooldown(
        1,
        60,
        commands.BucketType.user
    )
    async def install(
        self,
        ctx,
        package: str
    ):
        """
        Install a Python package into the bot venv.

        Example:
        !install beautifulsoup4
        """

        # Validate package name
        if not re.fullmatch(
            r"[a-zA-Z0-9._-]+",
            package
        ):
            await ctx.send(
                "Invalid package name."
            )
            return

        # Check venv exists
        if not VENV_PYTHON.exists():
            await ctx.send(
                "Bot virtual environment not found."
            )
            return

        message = await ctx.send(
            f"🔄 Installing `{package}`..."
        )

        code, output = await self.run_command(
            str(VENV_PYTHON),
            "-m",
            "pip",
            "install",
            package
        )

        if code != 0:
            await message.edit(
                content=(
                    f"Failed installing `{package}`.\n"
                    f"```text\n"
                    f"{output[-1500:]}\n"
                    f"```"
                )
            )
            return

        await message.edit(
            content=(
                f"✅ Installed `{package}`.\n"
                f"```text\n"
                f"{output[-1500:]}\n"
                f"```"
            )
        )

    @commands.command(
        name="packages",
        hidden=True
    )
    @commands.is_owner()
    @commands.cooldown(
        1,
        30,
        commands.BucketType.user
    )
    async def packages(
        self,
        ctx
    ):
        """
        Show installed packages.
        """

        if not VENV_PYTHON.exists():
            await ctx.send(
                "❌ Bot virtual environment not found."
            )
            return

        message = await ctx.send(
            "Checking packages..."
        )

        code, output = await self.run_command(
            str(VENV_PYTHON),
            "-m",
            "pip",
            "list"
        )

        if code != 0:
            await message.edit(
                content=(
                    "Could not retrieve packages.\n"
                    f"```text\n{output[-1500:]}\n```"
                )
            )
            return

        await message.edit(
            content=(
                "📦 Installed packages:\n"
                f"```text\n{output[-1800:]}\n```"
            )
        )

    @commands.command(
        name="upgrade",
        hidden=True
    )
    @commands.is_owner()
    @commands.cooldown(
        1,
        60,
        commands.BucketType.user
    )
    async def upgrade(
        self,
        ctx,
        package: str
    ):
        """
        Upgrade a Python package.
        """

        if not re.fullmatch(
            r"[a-zA-Z0-9._-]+",
            package
        ):
            await ctx.send(
                "Invalid package name."
            )
            return

        message = await ctx.send(
            f"⬆️ Upgrading `{package}`..."
        )

        code, output = await self.run_command(
            str(VENV_PYTHON),
            "-m",
            "pip",
            "install",
            "--upgrade",
            package
        )

        if code != 0:
            await message.edit(
                content=(
                    f"Upgrade failed for `{package}`.\n"
                    f"```text\n{output[-1500:]}\n```"
                )
            )
            return

        await message.edit(
            content=(
                f"✅ Upgraded `{package}`.\n"
                f"```text\n{output[-1500:]}\n```"
            )
        )


async def setup(bot):
    await bot.add_cog(PipInstaller(bot))