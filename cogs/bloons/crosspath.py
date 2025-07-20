from datetime import datetime
import discord
from discord.ext import commands
from utils.bloons import MONKEYS, MONKEY_IMAGES
from itertools import product
from utils.embedbuilder import EmbedBuilder
from utils.types import EmbedResult

class Crosspath(commands.Cog):

    @staticmethod
    async def get_bloons_crosspath(db, monkey_key: str) -> dict:
        row = await db.fetchrow("""
            SELECT top, mid, bot, last_modified_by, last_modified_at
            FROM crosspaths
            WHERE monkey = $1
        """, monkey_key)

        if row:
            return {
                "paths": {
                    "top": row["top"].split() if row["top"] else [],
                    "mid": row["mid"].split() if row["mid"] else [],
                    "bot": row["bot"].split() if row["bot"] else [],
                },
                "last_modified_by": row["last_modified_by"],
                "last_modified_at": row["last_modified_at"].isoformat() if row["last_modified_at"] else None,
            }

        return {
            "paths": {"top": [], "mid": [], "bot": []},
            "last_modified_by": "Unknown",
            "last_modified_at": None,
        }

    @staticmethod
    def get_valid_crosspaths(path: str) -> set[str]:
        path_index = {"top": 0, "mid": 1, "bot": 2}[path]
        valid = {
            f"{t}{m}{b}"
            for t, m, b in product(range(6), repeat=3)
            if [t, m, b][path_index] >= max([t, m, b][:path_index] + [t, m, b][path_index+1:])
        }
        return valid

    @staticmethod
    def build_embed(monkey_name: str, meta: dict, record: dict) -> EmbedResult:
        embed = (
            EmbedBuilder()
            .author(name=f"{monkey_name} Crosspath", icon="ninjakiwi")
            .thumbnail(url=MONKEY_IMAGES.get(monkey_name, ""))
        )

        for label, icon_key, path_key in [
            ("Top", "path1", "top"),
            ("Mid", "path2", "mid"),
            ("Bot", "path3", "bot"),
        ]:
            icon = meta[icon_key]
            value = record["paths"].get(path_key)
            display = ", ".join(value) if value else "Not set"
            embed.field(name=label, value=f"{icon}  `{display}`", inline=False)

        editor = record.get("last_modified_by", "Unknown")
        embed.footer(text=f"Last edited by {editor}")

        timestamp = record.get("last_modified_at")
        if timestamp:
            try:
                embed.timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                pass

        return embed, False

    @staticmethod
    async def from_monkey(db, monkey_choice) -> EmbedResult:
        name = monkey_choice.value
        key = name.lower()
        meta = MONKEYS[name]
        record = await Crosspath.get_bloons_crosspath(db, key)
        return Crosspath.build_embed(name, meta, record)

    @staticmethod
    async def update_record(db, monkey_key: str, user: discord.User,top: str = None, mid: str = None, bot: str = None) -> EmbedResult:
        if not any([top, mid, bot]):
            return (
                EmbedBuilder(description="You must provide at least one path to update (top, mid, or bot)."),
                False,
            )

        # Fetch existing record to preserve unchanged paths
        existing_record = await Crosspath.get_bloons_crosspath(db, monkey_key)
        existing_paths = existing_record["paths"]

        inputs = {"top": top, "mid": mid, "bot": bot}
        paths = {}

        for path_key, raw in inputs.items():
            if not raw:
                # Keep existing if no new input
                paths[path_key] = " ".join(existing_paths[path_key])
                continue

            valid_set = Crosspath.get_valid_crosspaths(path_key)
            raw_split = raw.split()
            valid = [code for code in raw_split if code in valid_set]
            invalid = [code for code in raw_split if code not in valid_set]

            if invalid:
                return  (
                    EmbedBuilder(description=f"Invalid {path_key} path(s): {' '.join(invalid)}\n"
                    f"Allowed pattern: 3-digit integers like 520, 302, etc."),
                    False,
                )

            paths[path_key] = " ".join(valid)

        await db.execute("""
            INSERT INTO crosspaths (monkey, top, mid, bot, last_modified_by, last_modified_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (monkey) DO UPDATE SET
                top = EXCLUDED.top,
                mid = EXCLUDED.mid,
                bot = EXCLUDED.bot,
                last_modified_by = EXCLUDED.last_modified_by,
                last_modified_at = EXCLUDED.last_modified_at
        """, monkey_key, paths["top"], paths["mid"], paths["bot"],
            user.display_name, datetime.utcnow())
        
        embed = EmbedBuilder(description=f"✅ Updated crosspaths for **{monkey_key.title()}")

        return embed, True


async def setup(bot):
    await bot.add_cog(Crosspath(bot))
