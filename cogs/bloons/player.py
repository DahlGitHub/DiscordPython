from typing import Tuple, Union
from datetime import datetime, timedelta, timezone
from discord.ext import commands
import aiohttp
import discord

from utils.constraints import BLOONS_POPPED, GAMEPLAY
from utils.embedbuilder import EmbedBuilder
from utils.types import UserDataResult, EmbedResult


class Player(commands.Cog):

    @staticmethod
    async def fetch_user_btd6_data(db, user: discord.User | None = None) -> UserDataResult:

        try:
            success, data = await Player.get_bloons_key(db, user)
        except Exception as e:
            return (
                None,
                EmbedBuilder(description=f"Unexpected error: {e}"), 
                True
            )
        
        if not success:
            return (
                None,
                EmbedBuilder(description=data), 
                True
            )
        return user, data, False

    @staticmethod
    async def get_bloons_key(db, user: discord.User) -> Tuple[bool, Union[dict, str]]:
        row = await db.fetchrow(
            "SELECT key, timestamp FROM bloons_key WHERE user_id = $1", user.id
        )
        if not row:
            return (
                False, f"No BTD6 key found for {user.mention}."
            )

        key, timestamp = row["key"], row["timestamp"]
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        if timestamp < datetime.now(timezone.utc) - timedelta(days=90):
            return (
                False, f"⚠️ The BTD6 key for {user.mention} is expired."
            )

        url = f"https://data.ninjakiwi.com/btd6/users/{key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return (
                        False, f"Could not reach BTD6 API."
                    )

                data = await response.json()
                if not data.get("success"):
                    return (
                        False, f"Invalid key or user does not play BTD6."
                    )

                return True, data["body"]

    @staticmethod
    async def bloons_stats(db, user: discord.User | None = None) -> EmbedResult:
        target_user, data, ephemeral = await Player.fetch_user_btd6_data(db, user)
        if not isinstance(data, dict):
            return data, ephemeral

        embed = EmbedBuilder()
        embed.author(
            name=f"{target_user.display_name}'s BTD6 Profile",
            icon=target_user.display_avatar.url,
        )
        embed.field(name="Name", value=data["displayName"], inline=False)
        embed.field(name="Rank", value=data["rank"], inline=True)
        embed.field(name="Achievements", value=data["achievements"], inline=True)
        embed.field(name="Most Played", value=data["mostExperiencedMonkey"], inline=True)
        embed.field(name="Highest Round", value=data["highestRound"], inline=True)
        embed.field(name="Followers", value=data["followers"], inline=True)
        embed.thumbnail(url=data["avatarURL"])
        embed.image(url=data["bannerURL"])

        return embed, ephemeral

    @staticmethod
    async def bloons_popped(db, user: discord.User | None = None) -> EmbedResult:
        target_user, data, ephemeral = await Player.fetch_user_btd6_data(db, user)

        if not isinstance(data, dict):
            return data, ephemeral

        bloons = data.get("bloonsPopped", {})
        embed = EmbedBuilder()
        embed.author(
            name=f"{target_user.display_name}'s Bloons Popped Stats",
            icon=target_user.display_avatar.url,
        )
        embed.footer(text="Ninjakiwi API", icon="ninjakiwi")

        labels = []
        values = []

        for key, label in BLOONS_POPPED.items():
            labels.append(label)
            values.append(f"{bloons.get(key, 0):,}")

        embed.field(name="Type", value="\n".join(labels), inline=True)
        embed.field(name="Popped", value="\n".join(values), inline=True)

        return embed, ephemeral

    @staticmethod
    async def bloons_towers(db, user: discord.User | None = None) -> EmbedResult:
        target_user, data, ephemeral = await Player.fetch_user_btd6_data(db, user)
        if not isinstance(data, dict):
            return data, ephemeral

        towers = data.get("towersPlaced", {})
        embed = EmbedBuilder()

        names = []
        counts = []

        for key, count in towers.items():
            names.append(key)
            counts.append(f"{count:,}")

        embed.field(name="Monkey", value="\n".join(names), inline=True)
        embed.field(name="Placed", value="\n".join(counts), inline=True)

        embed.author(
            name=f"{target_user.display_name}'s Monkeys Placed",
            icon=target_user.display_avatar.url,
        )
        embed.footer(text="Ninjakiwi API", icon="ninjakiwi")

        return embed, ephemeral
    
    @staticmethod
    async def bloons_heroes(db, user: discord.User | None = None) -> EmbedResult:
        target_user, data, ephemeral = await Player.fetch_user_btd6_data(db, user)
        if not isinstance(data, dict):
            return data, ephemeral

        heroes = data.get("heroesPlaced", {})
        embed = EmbedBuilder()

        names = []
        counts = []

        for key, count in heroes.items():
            names.append(key)
            counts.append(f"{count:,}")

        embed.field(name="Hero", value="\n".join(names), inline=True)
        embed.field(name="Placed", value="\n".join(counts), inline=True)

        embed.author(
            name=f"{target_user.display_name}'s Hero Placed",
            icon=target_user.display_avatar.url,
        )
        embed.footer(text="Ninjakiwi API", icon="ninjakiwi")

        return embed, ephemeral
    
    @staticmethod
    async def bloons_medals(db, user: discord.User | None = None) -> EmbedResult:
        target_user, data, ephemeral = await Player.fetch_user_btd6_data(db, user)
        if not isinstance(data, dict):
            return data, ephemeral

        sp_medals = data.get("_medalsSinglePlayer", {})
        mp_medals = data.get("_medalsMultiplayer", {})

        all_keys = sorted(set(sp_medals) | set(mp_medals))

        names = ""
        singles = ""
        multis = ""

        for key in all_keys:
            names += f"{key}\n"
            singles += f"{sp_medals.get(key, 0):,}\n"
            multis += f"{mp_medals.get(key, 0):,}\n"

        embed = (
            EmbedBuilder()
            .author(
                name=f"{target_user.display_name}'s Medals",
                icon=target_user.display_avatar.url,
            )
            .field(name="Mode", value=names.strip(), inline=True)
            .field(name="Single", value=singles.strip(), inline=True)
            .field(name="Multi", value=multis.strip(), inline=True)
        )
        embed.footer(text="Ninjakiwi API", icon="ninjakiwi")

        return embed, ephemeral

    @staticmethod
    async def bloons_gameplay(db, user: discord.User | None = None) -> EmbedResult:
        target_user, data, ephemeral = await Player.fetch_user_btd6_data(db, user)
        if not isinstance(data, dict):
            return data, ephemeral
        
        embed = EmbedBuilder()
        for key, label in GAMEPLAY.items():
            count = data["gameplay"].get(key, 0)
            embed.field(name=label, value=f"{count:,}", inline=True)

        embed.author(
            name=f"{target_user.display_name}'s Tower's Placed",
            icon=target_user.display_avatar.url,
        )
        embed.footer(text="Ninjakiwi API", icon="ninjakiwi")

        return embed, ephemeral


async def setup(bot):
    await bot.add_cog(Player(bot))
