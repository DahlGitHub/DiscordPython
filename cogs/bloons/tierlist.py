from discord.ext import commands
import aiohttp
from utils.bloons import TIERLIST
from utils.embedbuilder import EmbedBuilder
from utils.types import EmbedResult

class Tierlist(commands.Cog):

    @staticmethod
    async def fetch_url(url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url + ".json", headers={"User-Agent": "BTD6 Tierlist"}
            ) as response:
                data = await response.json()
                try:
                    return data[0]["data"]["children"][0]["data"]["url"]
                except Exception:
                    return "https://demofree.sirv.com/nope-not-here.jpg"

    @staticmethod
    async def bloons_tierlist(version: int | None = None) -> EmbedResult:
        if version is None:
            version = len(TIERLIST) - 1

        if version < 0 or version >= len(TIERLIST):
            return (
                EmbedBuilder(description=f"Version {version} doesn't exists."),
                True,
            )

        entry = TIERLIST[version]

        if not isinstance(entry, str) or not entry.startswith("http"):
            return (
                EmbedBuilder(description=f"There's no tierlist for version {version}"),
                True,
            )

        image_url = await Tierlist.fetch_url(entry)

        embed = (
            EmbedBuilder()
            .author(name=f"BTD6 Tier List v{version}", icon="ninjakiwi")
            .image(url=image_url)
        )

        return embed, False


async def setup(bot: commands.Bot):
    await bot.add_cog(Tierlist(bot))
