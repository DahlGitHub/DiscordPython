import discord
from discord.ext import commands
from utils.embedbuilder import EmbedBuilder
from utils.types import EmbedResult
import json
from utils.paginator import ButtonPaginator
from utils.constraints import OFFICIAL_TOTALS, GEN_NAME_MAP, REGIONAL_TOTALS, TYPE_EMOJIS, TYPE_COLORS

class List(commands.Cog):
    with open("json/cobblemon.json", "r", encoding="utf-8") as f:
        pokedata: list[dict] = json.load(f)

    @staticmethod
    async def cobblemon_list() -> EmbedResult:
        pokedata = List.pokedata
        gen_counts = {gen: {"implemented": 0, "obtainable": 0, "regionals": 0} for gen in OFFICIAL_TOTALS}
        regional_variants = 0
        unobtainable = []
        alola_bias = []
        hisui_bias = []

        for p in pokedata:
            gen = p["Gen"]
            name = p["Name"]
            obtainable = p["Obtainable"]

            is_regional = "(" in name

            if gen in OFFICIAL_TOTALS:
                if is_regional:
                    gen_counts[gen]["regionals"] += 1
                    regional_variants += 1
                else:
                    gen_counts[gen]["implemented"] += 1

                if obtainable:
                    gen_counts[gen]["obtainable"] += 1

            elif gen == "":
                if "(Alola)" in name:
                    alola_bias.append(name)
                elif "(Hisui)" in name:
                    hisui_bias.append(name)

            if not obtainable:
                unobtainable.append(name)

        desc_lines = []

        for gen, title in GEN_NAME_MAP.items():
            total = OFFICIAL_TOTALS[gen]
            reg_x, reg_y = REGIONAL_TOTALS.get(gen, (0, 0))
            g = gen_counts[gen]
            regional_note = f" (+{reg_x}/{reg_y} regional forms)" if reg_x else ""
            desc_lines.append(
                f"<:cobblemonblue:1397547128192237690> **{title}**:\n"
                f"{g['implemented']}/{total}{regional_note} ({g['obtainable']} obtainable)"
            )

        desc_lines.append(
            f"<:cobblemonpurple:1397547126434828309> **Total number of Pokémon:**\n"
            f"{sum(g['implemented'] for g in gen_counts.values())}/1025 Pokémon "
            f"(+{regional_variants}/57 regional variants) "
            f"({sum(g['obtainable'] for g in gen_counts.values())} obtainable)"
        )

        if hisui_bias or alola_bias:
            desc_lines.append("<:cobblemonyellow:1397547124396392460> **Cobblemon Original Regionals:**")
            if hisui_bias:
                hisui_clean = [name.replace(" (Hisui)", "") for name in hisui_bias]
                desc_lines.append(f"{len(hisui_bias)} Hisui-Bias ({', '.join(hisui_clean)})")
            if alola_bias:
                alola_clean = [name.replace(" (Alola)", "") for name in alola_bias]
                desc_lines.append(f"{len(alola_bias)} Alola-Bias ({', '.join(alola_clean)})")


        embed = EmbedBuilder(
            description=f"\n".join(desc_lines)
        )
        embed.author(name="Cobblemon Pokémon List", icon="cobblemon")

        if unobtainable:
            embed.footer(
                text=f"Currently unobtainable in base mod: {', '.join(unobtainable)}",
                icon="cobblemon"
            )

        return embed, False

    @staticmethod
    async def cobblemon_types(type: str) -> tuple[list[discord.Embed], bool]:
        type = type.lower()
        if type not in TYPE_EMOJIS:
            embed = discord.Embed(description=f"Unknown type: {type}")
            return [embed], True

        pokedata = List.pokedata

        filtered = [
            p for p in pokedata
            if type in (
                p.get("Type 1", "").lower(),
                p.get("Type 2", "").lower()
            ) and p.get("Obtainable") is True
        ]

        if not filtered:
            embed = discord.Embed(description=f"No Pokémon found for type: {type}")
            return [embed], True

        # Break into pages of 20
        per_page = 20
        pages = []
        total = len(filtered)

        for i in range(0, total, per_page):
            chunk = filtered[i:i+per_page]

            lines = []
            for j, p in enumerate(chunk):
                other_type = None
                if p["Type 1"].lower() == type and p["Type 2"].lower() not in ("-", type):
                    other_type = p["Type 2"].lower()
                elif p["Type 2"].lower() == type and p["Type 1"].lower() not in ("-", type):
                    other_type = p["Type 1"].lower()

                other_emoji = TYPE_EMOJIS.get(other_type, "") if other_type else ""
                extra = f" {other_emoji}" if other_emoji else ""
                lines.append(f"{i + j + 1}. {p['Name']} ({p['ID']}){extra}")
            header = f"**{TYPE_EMOJIS[type]} {type.capitalize()} Pokémon**"
            body = "\n".join(lines)
            embed_color = TYPE_COLORS.get(type, discord.Color.brand_red())
            embed = discord.Embed(
                description=f"{header}\n{body}", color=embed_color
            )
            embed.set_author(name="Cobblemon Pokémon Types", icon_url="https://cdn.discordapp.com/attachments/1155038652137734236/1397547506467864648/1117423483190788158.webp?ex=68821f0a&is=6880cd8a&hm=6612ef4cdf1242b0b5a14b4838adc0581450e2865393eabf1477f3b8bcdde8db&")  # Set an icon_url if needed
            embed.set_footer(text=f"Page {i//per_page + 1}/{-(-total//per_page)} ({total} total)")
            pages.append(embed)

        return pages, False

async def setup(bot: commands.Bot):
    await bot.add_cog(List(bot))
