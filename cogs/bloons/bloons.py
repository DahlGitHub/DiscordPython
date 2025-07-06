import discord
from discord.ext import commands
from discord import app_commands
from utils.bloons import MONKEYS
from .crosspath import Crosspath
from .player import Player
from .tierlist import Tierlist


class Bloons(commands.GroupCog, name="bloons" ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """
    Crosspath.py

    Display and set a list of crosspaths for the monkey towers
    """

    @app_commands.command(name="crosspath", description="View recommended crosspaths for a monkey")
    @app_commands.choices(monkey=[app_commands.Choice(name=name, value=name) for name in MONKEYS])
    async def crosspath(self, interaction: discord.Interaction, monkey: app_commands.Choice[str]):
        embed = Crosspath.from_monkey(monkey, self.get_bloons_crosspath)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="editcrosspath", description="Edit the crosspaths for a monkey")
    @app_commands.describe(monkey="Choose the monkey",top="Top",mid="Mid",bot="Bot")
    @app_commands.choices(monkey=[app_commands.Choice(name=name, value=name) for name in MONKEYS])
    async def crosspath_edit(self,interaction: discord.Interaction,monkey: app_commands.Choice[str],top: str = None,mid: str = None,bot: str = None,):
        message = Crosspath.apply_edit(monkey, interaction.user, top, mid, bot)
        await interaction.response.send_message(message, ephemeral=True)

    """
    Tierlist.py
    
    Fetches a static tierlist, utilizes Reddit API for image from post.
    """

    @app_commands.command(name="tierlist", description="BTD6 Chimps Tierlist")
    async def tierlist(self, interaction: discord.Interaction, version: int = None):
        embed = await Tierlist.bloons_tierlist(version)
        await interaction.response.send_message(embed=embed)

    """
    Player.py 

    Fetches BTD6 Player data from Ninjakiwi API
    """
    player_api = app_commands.Group(name='player', description="Get data from Ninjakiwi API")
    @player_api.command(name="id", description="Set the ID for your BTD6 account")
    async def id(self, interaction: discord.Interaction, bloons_key: str):
        await self.bot.db.execute(
            "INSERT INTO bloons_key (user_id, key) VALUES ($1, $2)",
            interaction.user.id, bloons_key
        )
        await interaction.response.send_message(f"Your BTD6 account key has been set to: `{bloons_key}`", ephemeral=True)
    
    @player_api.command(name="stats")
    async def player(self, interaction: discord.Interaction, user: discord.User | None = None):
        embed = await Player.bloons_stats(self, interaction, user)
        await interaction.followup.send(embed=embed)

    @player_api.command(name="popped")
    async def popped(self, interaction: discord.Interaction, user: discord.User | None = None):
        embed = await Player.bloons_popped(self, interaction, user)
        await interaction.followup.send(embed=embed)

    @player_api.command(name="monkeys", description="Get the number of monkeys placed by a user")
    async def monkeys(self, interaction: discord.Interaction, user: discord.User | None = None):
        embed = await Player.bloons_towers(self, interaction, user)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Bloons(bot))
