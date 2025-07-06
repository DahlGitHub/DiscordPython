from datetime import datetime
import discord
from discord.ext import commands
from utils.bloons import MONKEYS

# Will handle database later...
monkey_data = {}

class Crosspath(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_valid_crosspaths(path: str) -> set[str]:
        patterns = {
            "top": ["{x}10", "{x}20", "{x}01", "{x}02"],
            "mid": ["1{x}0", "2{x}0", "01{x}", "02{x}"],
            "bot": ["10{x}", "20{x}", "01{x}", "02{x}"],
        }
        return {pattern.format(x=x) for x in range(1, 6) for pattern in patterns[path]}

    @staticmethod
    def build_embed(monkey_name: str, meta: dict, record: dict) -> discord.Embed:
        embed = discord.Embed(
            title=f"Crosspath Recommendations for {monkey_name}",
            color=discord.Color.orange()
        )
        embed.set_author(name="Monkey Crosspath")
        embed.set_thumbnail(url=meta["image"])

        for label, icon_key, path_key in [
            ("Top", "path1", "top"),
            ("Mid", "path2", "mid"),
            ("Bot", "path3", "bot"),
        ]:
            icon = meta[icon_key]
            value = record["paths"].get(path_key)
            display = ", ".join(value) if value else "Not set"
            embed.add_field(name=label, value=f"{icon}  `{display}`", inline=False)

        editor = record.get("last_modified_by", "Unknown")
        embed.set_footer(text=f"Last edited by {editor}")

        timestamp = record.get("last_modified_at")
        if timestamp:
            try:
                embed.timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                pass

        return embed
    
    @staticmethod
    def from_monkey(monkey_choice, fetch_func) -> discord.Embed:
        name = monkey_choice.value
        key = name.lower()
        meta = MONKEYS[name]
        record = fetch_func(key)
        return Crosspath.build_embed(name, meta, record)
    
    @staticmethod
    def update_record(monkey_key: str, user: discord.User, top: str = None, mid: str = None, bot: str = None) -> tuple[bool, str]:
        if not any([top, mid, bot]):
            return False, "⚠️ You must provide at least one path to update (top, mid, or bot)."

        record = monkey_data.setdefault(monkey_key, {
            "paths": {"top": [], "mid": [], "bot": []},
            "last_modified_by": None,
            "last_modified_at": None,
        })

        inputs = {"top": top, "mid": mid, "bot": bot}
        for path_key, raw in inputs.items():
            if not raw:
                continue

            valid_set = Crosspath.get_valid_crosspaths(path_key)
            raw_split = raw.split()
            valid = [code for code in raw_split if code in valid_set]
            invalid = [code for code in raw_split if code not in valid_set]

            if invalid:
                return False, (
                    f"❌ Invalid {path_key} path(s): {' '.join(invalid)}\n"
                    f"✅ Allowed pattern: X10, X20, X01, X02"
                )

            record["paths"][path_key] = valid

        record["last_modified_by"] = user.display_name
        record["last_modified_at"] = datetime.utcnow().isoformat()
        return True, f"✅ Updated crosspaths for **{monkey_key.title()}**."
    
    @staticmethod
    def apply_edit(monkey_choice, user, top=None, mid=None, bot=None) -> str:
        monkey_key = monkey_choice.value.lower()

        if not any([top, mid, bot]):
            return "⚠️ You must provide at least one path to update (top, mid, or bot)."

        record = monkey_data.setdefault(monkey_key, {
            "paths": {"top": [], "mid": [], "bot": []},
            "last_modified_by": None,
            "last_modified_at": None,
        })

        inputs = {"top": top, "mid": mid, "bot": bot}
        for path_key, raw in inputs.items():
            if not raw:
                continue

            valid_set = Crosspath.get_valid_crosspaths(path_key)
            raw_split = raw.split()
            valid = [code for code in raw_split if code in valid_set]
            invalid = [code for code in raw_split if code not in valid_set]

            if invalid:
                return (
                    f"❌ Invalid {path_key} path(s): {' '.join(invalid)}\n"
                    f"✅ Allowed pattern: X10, X20, X01, X02"
                )

            record["paths"][path_key] = valid

        record["last_modified_by"] = user.display_name
        record["last_modified_at"] = datetime.utcnow().isoformat()

        return f"✅ Updated crosspaths for **{monkey_choice.value}**."

async def setup(bot):
    await bot.add_cog(Crosspath(bot))