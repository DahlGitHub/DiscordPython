import discord
from discord.ext import commands
from discord import app_commands
from typing import List, Tuple, Optional, Dict

import config
from datetime import datetime, timezone, timedelta
import aiohttp
from utils.bloons import BLOONS_POPPED, TOWERS_PLACED
from discord.app_commands import Group


class Bloons(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_bloons_key(self, user: discord.User):
        bloons_key = await self.bot.db.fetchrow(
            "SELECT key, timestamp FROM bloons_key WHERE user_id = $1",
            user.id
        )

        if not bloons_key:
            return False, f"No BTD6 key found for {user.mention}."
        
        key, timestamp = bloons_key["key"], bloons_key["timestamp"]
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        if timestamp < datetime.now(timezone.utc) - timedelta(days=90):
            return False, f"⚠️ The BTD6 key for {user.mention} is expired."
        
        url = f"https://data.ninjakiwi.com/btd6/users/{key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False, "Could not reach BTD6 API. Try again later."
                
                player_data = await response.json()
                if not player_data.get("success"):
                    return False, "Invalid key or the user does not play BTD6."

                return True, player_data["body"]

    async def fetch_bloons_data(self, ctx: commands.Context, user: discord.User | None = None):
        target_user = user or ctx.author
        try:
            success, result = await self.get_bloons_key(target_user)
        except Exception as e:
            await ctx.send(f"Unexpected error while fetching profile: {e}")
            return None, None

        if not success:
            await ctx.send(result)
            return None, None

        return result, target_user


    @app_commands.command(name="id", description="Set the ID for your BTD6 account")
    @app_commands.describe(bloons_key="Your BTD6 account key")
    async def id(self, interaction: discord.Interaction, bloons_key: str):
        await self.bot.db.execute(
            "INSERT INTO bloons_key (user_id, key) VALUES ($1, $2)",
            interaction.user.id, bloons_key
        )
        await interaction.response.send_message(f"Your BTD6 account key has been set to: `{bloons_key}`", ephemeral=True)
    
    @app_commands.command(name="player", description="Hello")
    @app_commands.describe(user="The Discord user to check (optional)")
    async def player(self, interaction: discord.Interaction, user: discord.User | None = None):
        try:
            await interaction.response.defer(thinking=True)
        except discord.NotFound:
            return  # Gracefully exit if the interaction is already expired

        target_user = user or interaction.user

        try:
            success, result = await self.get_bloons_key(target_user)
        except Exception as e:
            return await interaction.followup.send(f"Unexpected error while fetching profile: {e}")

        if not success:
            try:
                return await interaction.followup.send(result)
            except discord.HTTPException:
                return  # Avoid crashing if followup fails

        user_data = result

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"{target_user.display_name}'s BTD6 Profile", icon_url=target_user.display_avatar.url)
        embed.add_field(name="Name", value=user_data['displayName'], inline=False)
        embed.add_field(name="Rank", value=user_data['rank'], inline=True)
        embed.add_field(name="Achievements", value=user_data['achievements'], inline=True)
        embed.add_field(name="Most Played", value=user_data['mostExperiencedMonkey'], inline=True)
        embed.add_field(name="Highest Round", value=user_data['highestRound'], inline=True)
        embed.add_field(name="Followers", value=user_data['followers'], inline=True)

        if 'avatarURL' in user_data:
            embed.set_thumbnail(url=user_data['avatarURL'])

        if 'bannerURL' in user_data:
            embed.set_image(url=user_data['bannerURL'])  # Optional: shows profile banner

        try:
            await interaction.followup.send(embed=embed)
        except discord.HTTPException:
            pass  # Avoid secondary error if already sent


    @app_commands.command(name="popped", description="Get the number of bloons popped by a user")
    async def popped(self, interaction : discord.Interaction, user: discord.User | None = None):
        """
        Get the number of bloons popped by a user.
        If no user is specified, defaults to the command invoker.
        """
        target_user = user or interaction.user

        try:
            success, result = await self.get_bloons_key(target_user)
        except Exception as e:
            return await interaction.response.send_message(f"Unexpected error while fetching profile: {e}")

        if not success:
            return await interaction.response.send_message(result)

        user_data = result

        # Assuming this is your data
        bloons = user_data["bloonsPopped"]

        # Loop through the map and add fields to embed
        embed = discord.Embed(color=discord.Color.green())
        for key, label in BLOONS_POPPED.items():
            count = bloons[key]
            embed.add_field(name=label, value=f"{count:,}", inline=True)
        embed.set_author(name=f"{target_user.display_name}'s Bloons Stats", icon_url=target_user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="monkeys", description="Get the number of monkeys placed by a user")
    async def monkeys(self, ctx: commands.Context, user: discord.User | None = None):
        """
        Get the number of monkeys placed by a user.
        """
        user_data, target_user = await self.fetch_bloons_data(ctx, user)
        if user_data is None:
            return

        embed = discord.Embed(color=discord.Color.blue())
        for key, label in TOWERS_PLACED.items():
            count = user_data["towersPlaced"].get(key, 0)
            embed.add_field(name=label, value=f"{count:,}", inline=True)
        embed.set_author(name=f"{target_user.display_name}'s Tower's Placed", icon_url=target_user.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Bloons(bot))
