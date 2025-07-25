import re
from typing import Optional, Tuple
import aiohttp
from discord import app_commands
from discord.ext import commands
from utils.constraints import WIKI_MONKEYS, WIKI_HEROES, MONKEY_IMAGES
from utils.embedbuilder import EmbedBuilder
from utils.types import EmbedResult

# Regex patterns and block headers
UPGRADE_LINE = re.compile(r"^\s*([0-5]{3})\s*$", re.M)
BASE_HDRS = {"__changes from 0-0-0__", "changes from 000:"}
TIER_HDRS = {"__changes from previous tier__", "changes from previous tier:"}
CROSS_HDRS = {"__crosspath changes__", "__crosspath benefits__", "crosspath benefits:"}


class Wiki(commands.Cog):
    """
    Fetches and parses BTD6 monkey and hero info from Pastebin entries.
    """
    @staticmethod
    async def fetch_url(url: str) -> str:

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                text = await resp.text()

        return text

    @staticmethod
    async def extract_upgrade_block(raw: str, code: str) -> Optional[str]:
        """Return the block whose first 3 chars == code (e.g. '310')."""
        parts = re.split(r"(?=^\s*[0-5]{3}\s*$)", raw, flags=re.M)
        for block in parts:
            if block.lstrip()[:3] == code:
                return block.strip()
        return None

    @staticmethod
    def split_bloonology(block: str) -> Tuple[str, str, str]:
        main, tier, cross = [], [], []
        target = main
        for line in block.splitlines():
            head = line.strip().lower()
            if head in BASE_HDRS or head in TIER_HDRS:
                target = tier
                continue
            if head in CROSS_HDRS:
                target = cross
                continue
            target.append(line.rstrip())
        return ("\n".join(p).strip() for p in (main, tier, cross))

    @staticmethod
    def extract_hero_level_block(raw: str, level: int) -> Tuple[str, str]:
        lines = raw.splitlines()
        start = None
        end = None

        for i, line in enumerate(lines):
            if line.strip().lower() == f"level {level}":
                start = i
            elif start is not None and (
                line.strip().lower().startswith("level ")
                or line.strip().lower().startswith("all levels")
            ):
                end = i
                break

        if start is None:
            return "", ""

        block = "\n".join(lines[start:end]).strip() if end else "\n".join(lines[start:]).strip()
        main, changes = [], []
        target = main
        for line in block.splitlines():
            if line.strip().lower() == "__changes from previous level__":
                target = changes
                continue
            target.append(line.rstrip())

        return ("\n".join(main).strip(), "\n".join(changes).strip())

    @staticmethod
    async def tower(
        monkey: app_commands.Choice[str],
        code: Optional[str] = None,
    ) -> EmbedResult:
        code = code or "000"
        url = WIKI_MONKEYS.get(monkey.value)

        if not url:
            return (
                EmbedBuilder(description=f"No Pastebin link found for {monkey.value}"),
                True
            )

        if not re.fullmatch(r"[0-5]{3}", code):
            return (
                EmbedBuilder(description="Upgrade code must be three digits 0–5 (e.g. `310`)."),
                True
            )

        raw = await Wiki.fetch_url(url)

        if code:
            block = await Wiki.extract_upgrade_block(raw, code)
            if block is None:
                return (
                    EmbedBuilder(description=f"No entry for `{code}` in the wiki for {monkey.value}."), 
                    True
                )
            main, tier, cross = Wiki.split_bloonology(block[3:].lstrip())
            title = f"{monkey.value} {code}"
        else:
            main, tier, cross = Wiki.split_bloonology(raw)
            title = f"{monkey.value} (Base Info)"

        embed = EmbedBuilder(description=main[:4096] or "—",)
        embed.footer(text="d:dmg • md:moab dmg • cd:ceram dmg • fd:fortified dmg • ld:lead dmg • p:pierce • r:range • j:projectiles • s:attack speed")
        embed.author(name=title, icon="ninjakiwi")
        embed.thumbnail(MONKEY_IMAGES.get(monkey.value))

        if tier:
            embed.field(name="Changes from Previous Tier", value=tier[:1024], inline=False)
        if cross:
            embed.field(name="Cross-path Benefits", value=cross[:1024], inline=False)

        return embed, False

    @staticmethod
    async def hero(
        hero: app_commands.Choice[str],
        level: Optional[app_commands.Range[int, 1, 20]] = None,
    ) -> EmbedResult:
        url = WIKI_HEROES.get(hero.value)
        if not url:
            return (
                EmbedBuilder(description=f"No Pastebin link found for {hero.value}"),
                True
            )

        raw = await Wiki.fetch_url(url)

        if level:
            main, changes = Wiki.extract_hero_level_block(raw, level)
            if not main:
                return (
                    EmbedBuilder(description=f"No data found for level {level}."),
                    True
                )
            title = f"{hero.value} – Level {level}"
            description = main[:4096]
        else:
            match = re.search(r"(?mi)^all levels\s*(.*)", raw, flags=re.DOTALL)
            if not match:
                return (
                    EmbedBuilder(description="No level 'all levels' found"),
                    True
                )
            title = f"{hero.value} – All Levels"
            description = match.group(1).strip()[:4096]
            changes = None

        embed = EmbedBuilder(description=description or "—")
        embed.author(name=title, icon="ninjakiwi")
        embed.thumbnail(url=MONKEY_IMAGES.get(hero.value))
        embed.footer(
            text="d:dmg • md:moab dmg • cd:ceram dmg • fd:fortified dmg • ld:lead dmg • p:pierce • r:range • j:projectiles • s:attack speed"
        )

        if level and changes:
            embed.field(
                name="Changes from Previous Level",
                value=changes[:1024] or "—",
                inline=False
            )

        return embed, False


async def setup(bot: commands.Bot):
    await bot.add_cog(Wiki(bot))
