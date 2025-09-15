from discord.ext import commands
from utils.embedbuilder import EmbedBuilder
import json
import aiohttp
import discord
from utils.types import PaginationResult
from utils.constraints import TYPE_EMOJIS, TYPE_COLORS, TYPE_EFFECTIVENESS 
from utils.cobblemonformat import (    
    group_spawns,
    format_effectiveness,
    format_drops,
    format_evolutions,
    format_conditions,
    format_multipliers,
    format_biomes,
    format_abilities,
)
class Pokedex(commands.Cog):

    _data: list[dict] = []
    _names: list[str] = []

    @staticmethod
    def _load():
        if not Pokedex._data:
            with open("json/cobblemon.json", "r", encoding="utf-8") as f:
                Pokedex._data = json.load(f)
                Pokedex._names = [entry["Name"] for entry in Pokedex._data]

    @staticmethod
    def get_base_names() -> list[str]:
        Pokedex._load()
        return [e["Name"] for e in Pokedex._data if "(" not in e["Name"]]

    @staticmethod
    def get_entry(name: str) -> dict | None:
        Pokedex._load()
        return next((e for e in Pokedex._data if e["Name"].lower() == name.lower()), None)

    @staticmethod
    async def fetch_json(url: str) -> dict | None:
        if not url:
            return None
        raw_url = url.replace("/blob/", "/raw/")
        async with aiohttp.ClientSession() as session:
            async with session.get(raw_url) as resp:
                if resp.status == 200:
                    try:
                        text = await resp.text()
                        data = json.loads(text)
                        return data
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON: {e}")
                else:
                    print(f"HTTP error: {resp.status}")
                return None

    @staticmethod
    def make_error_embed(message: str) -> PaginationResult:
        return [EmbedBuilder(description=message)], True

    @staticmethod
    async def moves(name: str) -> PaginationResult:
        entry = Pokedex.get_entry(name)
        entry = Pokedex.get_entry(name)
        if not entry:
            return Pokedex.make_error_embed(f"No moves data found for '{name}'.")
        if not entry.get("Obtainable", True):
            return Pokedex.make_error_embed(f"**{name}** is not obtainable in Cobblemon.")
        if not entry.get("Data"):
            return Pokedex.make_error_embed(f"No data available for '{name}'.")

        data = await Pokedex.fetch_json(entry["Data"])
        if not data or "moves" not in data or not isinstance(data["moves"], list):
            return Pokedex.make_error_embed(f"No valid moves found for '{name}'.")

        moves = data["moves"]
        per_page = 20
        pages = []
        total = len(moves)

        for i in range(0, total, per_page):
            chunk = moves[i:i + per_page]
            move_lines = [f"{i + j + 1}. `{m}`" for j, m in enumerate(chunk)]

            embed = EmbedBuilder(
                description="\n".join(move_lines),
            )
            embed.author(name=f"{name} Moves", icon="cobblemon")
            embed.thumbnail(url=entry.get("Image"))
            embed.footer(text=f"Page {i // per_page + 1}/{-(-total // per_page)} ({total} moves)")
            pages.append(embed)

        return pages, False

    @staticmethod
    async def cobblemon_pokedex(name: str) -> PaginationResult:
        entry = Pokedex.get_entry(name)
        if not entry or not entry.get("Obtainable", True) or not entry.get("Data"):
            return Pokedex.make_error_embed(f"No data found for '{name}'.")

        data = await Pokedex.fetch_json(entry["Data"])
        if not data:
            return Pokedex.make_error_embed(f"No data file found for '{name}'.")

        # Type info
        primary = data.get("primaryType", "unknown").lower()
        secondary = data.get("secondaryType", "").lower()
        color = TYPE_COLORS.get(primary, discord.Color.dark_gray())
        type_str = f"{TYPE_EMOJIS.get(primary)} **{primary.capitalize()}**"
        if secondary:
            type_str += f" / {TYPE_EMOJIS.get(secondary)} **{secondary.capitalize()}**"

        abilities = format_abilities(data.get("abilities", []))
        gender_ratio = data.get("maleRatio", 0.875)
        male_pct = int(gender_ratio * 100)
        female_pct = 100 - male_pct
        egg_groups = ", ".join(data.get("eggGroups", [])) or "N/A"
        stats = data.get("baseStats", {})
        total_stats = sum(stats.values())
        effectiveness = format_effectiveness(primary, secondary)
        evolution_text = format_evolutions(data.get("evolutions", []))


        embed1 = discord.Embed(color=color)
        embed1.set_author(name=f"{name} — Base Info", icon_url="https://cdn.discordapp.com/emojis/1117423483190788158.webp")
        embed1.set_thumbnail(url=entry.get("Image"))
        embed1.description = (
            f"{type_str}\n\n"
            f"**Abilities:** {abilities}\n"
            f"**Gender Ratio:** `♂ {male_pct}%` / `♀ {female_pct}%`\n"
            f"**Catch Rate:** {data.get('catchRate', '?')}\n\n"
            f"{effectiveness}\n\n"
            f"**Base Stats:** ({total_stats})\n"
            f"HP: {stats.get('hp', '?')} | Atk: {stats.get('attack', '?')} | Def: {stats.get('defence', '?')}\n"
            f"SpA: {stats.get('special_attack', '?')} | SpD: {stats.get('special_defence', '?')} | Spe: {stats.get('speed', '?')}\n\n"
            f"**Height:** {data.get('height', 0)/10:.1f}m | **Weight:** {data.get('weight', 0)/10:.1f}kg\n\n"
            f"{evolution_text}"
        )
        embed1.set_footer(text="Page 1/2")

        evs = data.get("evYield", {})
        ev_text = ", ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in evs.items() if v > 0) or "None"
        drop_text = format_drops(data.get("drops", {}))
        labels = ", ".join(data.get("labels", [])) or "None"
        forms = ", ".join(f["name"] for f in data.get("forms", [])) or "None"

        embed2 = discord.Embed(color=color)
        embed2.set_author(name=f"{name} — Advanced Info", icon_url="https://cdn.discordapp.com/emojis/1117423483190788158.webp")
        embed2.set_thumbnail(url=entry.get("Image"))
        embed2.description = (
            f"**EV Yield:** {ev_text}\n"
            f"**Base EXP Yield:** {data.get('baseExperienceYield', '?')}\n"
            f"**Base Friendship:** {data.get('baseFriendship', '?')}\n"
            f"**Egg Cycles:** {data.get('eggCycles', '?')}\n"
            f"**Egg Groups:** {egg_groups}\n"
            f"**Labels:** {labels}\n"
            f"**Forms:** {forms}\n"
            f"**Drops:**\n{drop_text}"
        )
        embed2.set_footer(text="Page 2/2")

        return [embed1, embed2], False

    @staticmethod
    async def cobblemon_spawns(name: str) -> PaginationResult:
        entry = Pokedex.get_entry(name)
        if not entry:
            return Pokedex.make_error_embed(f"No spawn data found for '{name}'.")
        if not entry.get("Obtainable", True):
            return Pokedex.make_error_embed(f"**{name}** is not obtainable in Cobblemon.")
        if not entry.get("Spawns"):
            return Pokedex.make_error_embed(f"No spawn data available for '{name}'.")

        data = await Pokedex.fetch_json(entry["Spawns"])
        spawns = data.get("spawns") if data else None
        if not isinstance(spawns, list) or not spawns:
            return Pokedex.make_error_embed(f"No valid spawns found for '{name}'.")

        grouped_spawns = group_spawns(spawns)
        pages = []

        for idx, group in enumerate(grouped_spawns, 1):
            base = group["base"]

            context = base.get("context", "N/A")
            bucket = base.get("bucket", "N/A").replace("-", " ").capitalize()
            level = base.get("level", "N/A")
            weight = base.get("weight", 0)
            cond = base.get("condition", {})
            anticond = base.get("anticondition", {})

            biomes_text = format_biomes(cond.get("biomes", []))
            excluded_biomes_text = format_biomes(anticond.get("biomes", [])) if "biomes" in anticond else ""
            condition_lines = format_conditions(cond, anticond)
            multiplier_lines = format_multipliers(base)

            if multiplier_lines:
                condition_lines.append("\n**Multipliers:**")
                condition_lines.extend(multiplier_lines)

            description = (
                f"**Level:** {level}\n"
                f"**Rarity:** {bucket}, **Weight:** {weight}\n\n"
                f"**Biomes:**\n{biomes_text}\n"
            )

            if excluded_biomes_text:
                description += f"\n**Excluded Biomes:**\n{excluded_biomes_text}\n"

            if condition_lines:
                description += f"\n**Conditions:**\n" + "\n".join(condition_lines)

            embed = EmbedBuilder(description=description)
            embed.author(name=f"{name} Spawns — {context.capitalize()}", icon="cobblemon")
            embed.thumbnail(url=entry.get("Image"))
            embed.footer(text=f"Page {idx}/{len(grouped_spawns)}")
            pages.append(embed)

        return pages, False

async def setup(bot: commands.Bot):
    await bot.add_cog(Pokedex(bot))
