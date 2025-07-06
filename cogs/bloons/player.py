from datetime import datetime, timedelta, timezone
from discord.ext import commands
import aiohttp
import discord
from utils.bloons import BLOONS_POPPED, TOWERS_PLACED


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def fetch_user_btd6_data(self, interaction: discord.Interaction, user: discord.User | None = None) -> tuple[discord.User | None, dict | str]:
        try:
            await interaction.response.defer(thinking=True)
        except discord.NotFound:
            return None, "⚠️ Interaction expired."

        target = user or interaction.user

        try:
            success, data = await Player.get_bloons_key(self, target)
        except Exception as e:
            return None, f"❌ Unexpected error: {e}"

        if not success:
            return None, data

        return target, data

    @staticmethod
    async def get_bloons_key(self, user: discord.User):
        row = await self.bot.db.fetchrow("SELECT key, timestamp FROM bloons_key WHERE user_id = $1", user.id)
        if not row:
            return False, f"❌ No BTD6 key found for {user.mention}."

        key, timestamp = row["key"], row["timestamp"]
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        if timestamp < datetime.now(timezone.utc) - timedelta(days=90):
            return False, f"⚠️ The BTD6 key for {user.mention} is expired."

        url = f"https://data.ninjakiwi.com/btd6/users/{key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False, "❌ Could not reach BTD6 API."

                data = await response.json()
                if not data.get("success"):
                    return False, "❌ Invalid key or user does not play BTD6."

                return True, data["body"]

    @staticmethod
    async def bloons_stats(self, interaction: discord.Interaction, user: discord.User | None = None) -> discord.Embed | str:
        target_user, data = await Player.fetch_user_btd6_data(self, interaction, user)
        if isinstance(data, str):
            return data

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"{target_user.display_name}'s BTD6 Profile", icon_url=target_user.display_avatar.url)
        embed.add_field(name="Name", value=data['displayName'], inline=False)
        embed.add_field(name="Rank", value=data['rank'], inline=True)
        embed.add_field(name="Achievements", value=data['achievements'], inline=True)
        embed.add_field(name="Most Played", value=data['mostExperiencedMonkey'], inline=True)
        embed.add_field(name="Highest Round", value=data['highestRound'], inline=True)
        embed.add_field(name="Followers", value=data['followers'], inline=True)

        if 'avatarURL' in data:
            embed.set_thumbnail(url=data['avatarURL'])
        if 'bannerURL' in data:
            embed.set_image(url=data['bannerURL'])

        return embed

    @staticmethod
    async def bloons_popped(self, interaction: discord.Interaction, user: discord.User | None = None) -> discord.Embed | str:
        target_user, data = await Player.fetch_user_btd6_data(self, interaction, user)
        if isinstance(data, str):
            return data

        bloons = data.get("bloonsPopped", {})
        embed = discord.Embed(title="Bloons Popped", color=discord.Color.green())
        embed.set_author(name=f"{target_user.display_name}'s Bloons Stats", icon_url=target_user.display_avatar.url)

        for key, label in BLOONS_POPPED.items():
            embed.add_field(name=label, value=f"{bloons.get(key, 0):,}", inline=True)

        return embed
    
    @staticmethod
    async def bloons_towers(self, interaction: discord.Interaction, user: discord.User | None = None) -> discord.Embed | str:
        target_user, data = await Player.fetch_user_btd6_data(self, interaction, user)
        if isinstance(data, str):
            return data
        
        embed = discord.Embed(color=discord.Color.blue())
        for key, label in TOWERS_PLACED.items():
            count = data["towersPlaced"].get(key, 0)
            embed.add_field(name=label, value=f"{count:,}", inline=True)
        embed.set_author(name=f"{target_user.display_name}'s Tower's Placed", icon_url=target_user.display_avatar.url)
        
        return embed
    
async def setup(bot):
    await bot.add_cog(Player(bot))
