import asyncio
import sys
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


BOT_DIR = Path("/home/pi/DiscordPython")
VENV_PYTHON = BOT_DIR / "venv" / "bin" / "python"


async def is_bot_owner(interaction: discord.Interaction) -> bool:
    return await interaction.client.is_owner(interaction.user)


class GitHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def run_command(self, *args):
        """
        Run a shell command inside the bot repository.
        Returns:
            return_code, output
        """

        process = await asyncio.create_subprocess_exec(
            *args,
            cwd=BOT_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        stdout, _ = await process.communicate()

        output = stdout.decode(
            errors="replace"
        ).strip()

        return process.returncode, output

    @app_commands.command(name="pull", description="Pull the latest bot code and restart (owner only)")
    @app_commands.checks.cooldown(1, 30, key=lambda interaction: interaction.user.id)
    @app_commands.check(is_bot_owner)
    async def pull(self, interaction: discord.Interaction):
        """Pull the latest version from GitHub and restart the bot."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.edit_original_response(content="Checking GitHub...")

        code, status = await self.run_command(
            "git",
            "status",
            "--porcelain"
        )

        if code != 0:
            await interaction.edit_original_response(
                content=(
                    "Could not check Git status.\n"
                    f"```text\n{status[-1500:]}\n```"
                )
            )
            return

        if status:
            await interaction.edit_original_response(
                content=(
                    "Update cancelled because the Pi "
                    "has local changes:\n"
                    f"```text\n{status[-1500:]}\n```"
                )
            )
            return

        code, before = await self.run_command(
            "git",
            "rev-parse",
            "--short",
            "HEAD"
        )

        if code != 0:
            await interaction.edit_original_response(
                content=(
                    "Could not determine current commit.\n"
                    f"```text\n{before[-1500:]}\n```"
                )
            )
            return

        await interaction.edit_original_response(
            content="Pulling latest changes..."
        )

        code, pull_output = await self.run_command(
            "git",
            "pull",
            "--ff-only",
            "origin",
            "main"
        )

        if code != 0:
            await interaction.edit_original_response(
                content=(
                    "Git pull failed.\n"
                    f"```text\n{pull_output[-1500:]}\n```"
                )
            )
            return

        code, after = await self.run_command(
            "git",
            "rev-parse",
            "--short",
            "HEAD"
        )

        if code != 0:
            await interaction.edit_original_response(
                content=(
                    "Could not determine new commit.\n"
                    f"```text\n{after[-1500:]}\n```"
                )
            )
            return

        if before == after:
            await interaction.edit_original_response(
                content="Already up to date."
            )
            return

        requirements = BOT_DIR / "requirements.txt"

        if requirements.exists():

            await interaction.edit_original_response(
                content=(
                    f"`{before}` → `{after}`\n"
                    "Checking dependencies..."
                )
            )

            code, pip_output = await self.run_command(
                str(VENV_PYTHON),
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements)
            )

            if code != 0:
                await interaction.edit_original_response(
                    content=(
                        "Code was updated, but dependency "
                        "installation failed.\n\n"
                        "The bot will not restart.\n"
                        f"```text\n{pip_output[-1500:]}\n```"
                    )
                )
                return

        code, commit_message = await self.run_command(
            "git",
            "log",
            "-1",
            "--pretty=%s"
        )

        if code != 0:
            commit_message = "Unknown"

        embed = discord.Embed(
            title="Update successful",
            description=(
                "New code has been pulled.\n"
                "Restarting..."
            ),
            color=discord.Color.green()
        )

        embed.add_field(
            name="Version",
            value=f"`{before}` → `{after}`",
            inline=False
        )

        embed.add_field(
            name="Latest commit",
            value=discord.utils.escape_markdown(
                commit_message[:1024]
            ),
            inline=False
        )

        await interaction.edit_original_response(
            content=None,
            embed=embed
        )
        await self.bot.close()

        sys.exit(0)


async def setup(bot):
    await bot.add_cog(GitHub(bot))