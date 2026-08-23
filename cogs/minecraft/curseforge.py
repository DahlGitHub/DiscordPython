import aiohttp
import discord
from discord.ext import commands

import html
import re

import config
import utils.emotes as emotes


class Curseforge(commands.Cog):
    """
    CurseForge commands and API integration.
    """

    BASE_URL = "https://api.curseforge.com/v1"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context, project_id: int):

        headers = {
            "Accept": "application/json",
            "x-api-key": "$2a$10$EhfpMlBOynHhQUNQvnKGSOhMsXsjLZrKdvNzZMcxkL8t6snZsG3Va",
        }

        async with aiohttp.ClientSession() as session:

            # Get project
            async with session.get(
                f"{self.BASE_URL}/mods/{project_id}",
                headers=headers,
            ) as response:

                if response.status != 200:
                    await ctx.send(
                        f"CurseForge API failed: `{response.status}`"
                    )
                    return

                project_data = await response.json()

            project = project_data["data"]

            # Get latest file
            latest_files = project.get("latestFiles", [])

            if not latest_files:
                await ctx.send("No files found.")
                return

            latest = latest_files[0]
            file_id = latest["id"]

            # Get changelog
            async with session.get(
                f"{self.BASE_URL}/mods/"
                f"{project_id}/files/"
                f"{file_id}/changelog",
                headers=headers,
            ) as response:

                if response.status == 200:
                    changelog_data = await response.json()
                    changelog = changelog_data.get("data", "")
                else:
                    changelog = "No changelog available."

        # Convert common HTML formatting
        changelog = re.sub(
            r"<li[^>]*>",
            "• ",
            changelog,
            flags=re.IGNORECASE,
        )

        changelog = re.sub(
            r"</li>",
            "\n",
            changelog,
            flags=re.IGNORECASE,
        )

        changelog = re.sub(
            r"<br\s*/?>",
            "\n",
            changelog,
            flags=re.IGNORECASE,
        )

        changelog = re.sub(
            r"</?(?:p|h1|h2|h3|ul|ol)[^>]*>",
            "\n",
            changelog,
            flags=re.IGNORECASE,
        )

        # Remove remaining HTML tags
        changelog = re.sub(
            r"<[^>]+>",
            "",
            changelog,
        )

        # Decode HTML entities:
        # Pok&eacute;mon -> Pokémon
        # &nbsp; -> space
        changelog = html.unescape(changelog)

        # Clean whitespace
        changelog = re.sub(
            r"[ \t]+",
            " ",
            changelog,
        )

        changelog = re.sub(
            r"\n{3,}",
            "\n\n",
            changelog,
        )

        changelog = changelog.strip()

        if not changelog:
            changelog = "No changelog provided."

        # Embed field max is 1024 characters.
        if len(changelog) > 1000:
            changelog = (
                changelog[:1000].rsplit(" ", 1)[0]
                + "\n\n*...changelog truncated*"
            )

        version = latest.get(
            "displayName",
            "Unknown",
        )

        versions = ", ".join(
            latest.get("gameVersions", [])
        ) or "Unknown"

        release_types = {
            1: "Release",
            2: "Beta",
            3: "Alpha",
        }

        release_type = release_types.get(
            latest.get("releaseType"),
            "Unknown",
        )

        embed = discord.Embed(
            title=project["name"],
            url=project.get(
                "links",
                {},
            ).get("websiteUrl"),
            description=project.get(
                "summary",
                "",
            ),
            color=discord.Color.orange(),
        )

        embed.add_field(
            name="Latest Version",
            value=version,
            inline=False,
        )

        embed.add_field(
            name="Release Type",
            value=release_type,
            inline=True,
        )

        embed.add_field(
            name="Game Versions",
            value=versions,
            inline=True,
        )

        embed.add_field(
            name="Changelog",
            value=changelog,
            inline=False,
        )

        logo = project.get("logo")

        if logo:
            thumbnail = logo.get("thumbnailUrl")

            if thumbnail:
                embed.set_thumbnail(
                    url=thumbnail
                )

        embed.set_footer(
            text=f"Project ID: {project_id} • "
                 f"File ID: {file_id}"
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Curseforge(bot))