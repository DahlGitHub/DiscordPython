from discord.ext import commands
from utils.embedbuilder import EmbedBuilder
from utils.types import EmbedResult
import gspread
import config
import json
import re
import unicodedata

class FetchCobblemon(commands.Cog):

    @staticmethod
    def format_gitlab(name: str) -> str:
        name = re.sub(r"\(.*?\)", "", name)
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
        name = name.lower()
        name = re.sub(r'[^a-z]', '', name)
        return name

    @staticmethod
    def format_url(name: str) -> str:
        substitutions = {
            " (": "-",
            ")": "",
            "♀": "-f",
            "♂": "-m",
            "é": "e",
            "%": "",
            ":": "",
            "'": "",
            ".": "",
            " ": "-"
        }

        name = name.lower()
        for old, new in substitutions.items():
            name = name.replace(old, new)
        return name

    @staticmethod
    async def fetch_cobblemon_data() -> EmbedResult:
        data = gspread.service_account_from_dict(config.GSERVICE).open_by_url(config.GSPREAD_COBBLEMON).sheet1
        rows = data.get_all_values()

        columns = {
            0: "ID",
            2: "Name",
            3: "Gen",
            4: "Obtainable",
            5: "Type 1",
            6: "Type 2",
        }

        pokedata = []
        for row in rows[1:]:
            if len(row) < max(columns.keys()):
                continue

            entry = {key: row[idx].strip() for idx, key in columns.items()}

            if not entry["ID"] or not entry["ID"].startswith("#"):
                continue

            obtainable_raw = entry["Obtainable"].lower()
            obtainable = obtainable_raw in ["✓", "✔", "\u2714"]
            entry["Obtainable"] = obtainable

            name_formatted = FetchCobblemon.format_url(entry["Name"])
            gen = entry["Gen"]
            id_padded = entry["ID"].lstrip("#").zfill(4)

            entry["Image"] = f"https://www.smogon.com/forums/media/minisprites/{name_formatted}.png"

            if obtainable:
                entry["Data"] = (
                    f"https://gitlab.com/cable-mc/cobblemon/-/blob/main/common/src/main/resources/"
                    f"data/cobblemon/species/generation{gen}/{FetchCobblemon.format_gitlab(entry['Name'])}.json"
                )
                entry["Spawns"] = (
                    f"https://gitlab.com/cable-mc/cobblemon/-/blob/1.6.1/common/src/main/resources/"
                    f"data/cobblemon/spawn_pool_world/{id_padded}_{FetchCobblemon.format_gitlab(entry['Name'])}.json"
                )
            else:
                entry["Data"] = None
                entry["Spawns"] = None

            pokedata.append(entry)

        with open("json/cobblemon.json", "w", encoding="utf-8") as f:
            json.dump(pokedata, f, indent=2)

        embed = EmbedBuilder(description="Cobblemon data fetched and saved.")
        return embed, False


async def setup(bot: commands.Bot):
    await bot.add_cog(FetchCobblemon(bot))
