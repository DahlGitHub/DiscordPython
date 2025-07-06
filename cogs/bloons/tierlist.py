import discord
from discord.ext import commands
import aiohttp
from utils.bloons import TIERLIST

class Tierlist(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @staticmethod
    async def fetch_url(url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url + ".json", headers={"User-Agent": "BTD6 Tierlist"}) as response:
                data = await response.json()
                try:
                    return data[0]["data"]["children"][0]["data"]["url"]
                except Exception:
                    return "https://demofree.sirv.com/nope-not-here.jpg"

    @staticmethod
    async def bloons_tierlist(version: int | None = None) -> discord.Embed | str:
        if version is None:
            version = len(TIERLIST) - 1

        if version >= len(TIERLIST) or version < 0:
            return f"❌ Version {version} is out of range."

        entry = TIERLIST[version]

        if not isinstance(entry, str) or not entry.startswith("http"):
            return f"⚠️ No tier list found for version {version}: {entry}"

        image_url = await Tierlist.fetch_url(entry)

        embed = discord.Embed(title=f"BTD6 Tier List v{version}")
        embed.set_image(url=image_url)
        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Tierlist(bot))
