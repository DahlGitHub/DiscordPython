import discord
from discord.ext import commands
from discord import app_commands
from utils.constraints import MONKEYS, WIKI_HEROES, WIKI_MONKEYS
from .crosspath import Crosspath
from .player import Player
from .tierlist import Tierlist
from .wiki import Wiki


class Bloons(commands.GroupCog, name="bloons"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """
    Crosspath.py

    Display and set a list of crosspaths for the monkey towers
    """

    @app_commands.command(name="crosspath", description="View recommended crosspaths for a monkey")
    @app_commands.choices(monkey=[app_commands.Choice(name=name, value=name) for name in MONKEYS])
    async def crosspath(
        self, 
        interaction: discord.Interaction, 
        monkey: app_commands.Choice[str]
    ):
        embed, ephemeral = await Crosspath.from_monkey(self.bot.db, monkey)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @app_commands.command(name="editcrosspath", description="Edit the crosspaths for a monkey")
    @app_commands.describe(monkey="Choose the monkey", top="Top", mid="Mid", bot="Bot")
    @app_commands.choices(monkey=[app_commands.Choice(name=name, value=name) for name in MONKEYS])
    async def crosspath_edit(
        self,
        interaction: discord.Interaction,
        monkey: app_commands.Choice[str],
        top: str = None,
        mid: str = None,
        bot: str = None,
    ):
        embed, ephemeral = await Crosspath.update_record(self.bot.db, monkey.value.lower(), interaction.user, top, mid, bot)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    """
    Tierlist.py
    
    Fetches a static tierlist, utilizes Reddit API for image from post.
    """

    @app_commands.command(name="tierlist", description="BTD6 Chimps Tierlist")
    async def tierlist(
        self, 
        interaction: discord.Interaction, 
        version: int = None
    ):
        embed, ephemeral = await Tierlist.bloons_tierlist(version)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    """
    Wiki.py

    Fetches BTD6 data from Extreme Bloonology.
    """
    wiki = app_commands.Group(name="wiki", description="Get data from Bloonology")

    @wiki.command(name="monkey", description="Get info about a monkey tower")
    @app_commands.describe(monkey="Pick a monkey", code="Upgrade path (optional)")
    @app_commands.choices(monkey=[app_commands.Choice(name=name, value=name) for name in WIKI_MONKEYS])
    async def monkey(
        self,
        interaction: discord.Interaction,
        monkey: app_commands.Choice[str],
        code: str = "000",
    ):
        embed, ephemeral = await Wiki.tower(monkey, code)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @wiki.command(name="hero", description="Get info about a hero")
    @app_commands.describe(hero="Pick a hero", level="Optional level (1-20)")
    @app_commands.choices(hero=[app_commands.Choice(name=name, value=name) for name in WIKI_HEROES])
    async def hero(
        self,
        interaction: discord.Interaction,
        hero: app_commands.Choice[str],
        level: int = None,
    ):
        embed, ephemeral = await Wiki.hero( hero, level)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    """
    Player.py 

    Fetches BTD6 Player data from Ninjakiwi API
    """
    player_api = app_commands.Group(name="player", description="Get data from Ninjakiwi API")

    # Set ID to Database
    @player_api.command(name="id", description="Set the ID for your BTD6 account")
    async def id(
        self, 
        interaction: discord.Interaction, 
        bloons_key: str
    ):
        await self.bot.db.execute(
            "INSERT INTO bloons_key (user_id, key) VALUES ($1, $2)",
            interaction.user.id,
            bloons_key,
        )
        await interaction.response.send_message(f"Your BTD6 account key has been set to: `{bloons_key}`", ephemeral=True)

    # Fetches from Ninjakiwi API
    @player_api.command(name="stats", description="Get BTD6 player stats")
    async def player(self, interaction: discord.Interaction, user: discord.User | None = None):
        target = user or interaction.user
        embed, ephemeral = await Player.bloons_stats(self.bot.db, target)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @player_api.command(name="popped", description="Get BTD6 popped stats")
    async def popped(self, interaction: discord.Interaction, user: discord.User | None = None):
        target = user or interaction.user
        embed, ephemeral = await Player.bloons_popped(self.bot.db, target)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @player_api.command(name="monkeys", description="Get the number of monkeys placed by a user")
    async def monkeys(self, interaction: discord.Interaction, user: discord.User | None = None):
        target = user or interaction.user
        embed, ephemeral = await Player.bloons_towers(self.bot.db, target)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @player_api.command(name="heroes", description="Get the number of heroes placed by a user")
    async def heroes(self, interaction: discord.Interaction, user: discord.User | None = None):
        target = user or interaction.user
        embed, ephemeral = await Player.bloons_heroes(self.bot.db, target)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @player_api.command(name="medals", description="Get the number of medals by a user")
    async def medals(self, interaction: discord.Interaction, user: discord.User | None = None):
        target = user or interaction.user
        embed, ephemeral = await Player.bloons_medals(self.bot.db, target)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

async def setup(bot: commands.Bot):
    await bot.add_cog(Bloons(bot))
