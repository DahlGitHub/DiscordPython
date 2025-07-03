import discord
from discord.ext import commands
from discord import app_commands
from typing import List, Tuple, Optional, Dict

import config
from datetime import datetime, timezone, timedelta
import aiohttp
from utils.bloons import TIERLIST
from utils import EmbedBuilder

class Tierlist(commands.Cog):
    

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def fetchUrl(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url+".json", headers={"User-Agent":"BTD6 Tierlist"}) as response:
                data = await response.json()
                try:
                    image_url = data[0]["data"]["children"][0]["data"]["url"]
                    return image_url
                except Exception:
                    return "https://demofree.sirv.com/nope-not-here.jpg"

    @app_commands.command(name="bloonstierlist")
    async def tierlist(self, interaction : discord.Interaction, version: int = None):
        if version is None:
            version = len(TIERLIST) - 1

        if version >= len(TIERLIST) or version < 0:
            await interaction.response.send_message(f"❌ Version {version} is out of range.")
            return

        entry = TIERLIST[version]

        if not isinstance(entry, str) or not entry.startswith("http"):
            await interaction.response.send_message(f"⚠️ No tier list found for version {version}: {entry}")
            return

        image_url = await self.fetchUrl(entry)

        embed = discord.Embed(title=f"BTD6 Tier List v{version}")
        embed.set_image(url=image_url)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="add")
    async def add(self, ctx: commands.Context, url: str):
        await ctx.send(f"Would have added: {url}")

    @commands.command(name="remove")
    async def remove(self, ctx: commands.Context, version: int):
        await ctx.send(f"Would have removed version {version}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tierlist(bot))
