import discord
from discord.ext import commands
from discord import app_commands
from .fetchcobblemon import FetchCobblemon
from .list import List
from utils.paginator import ButtonPaginator
from .list import TYPE_EMOJIS
from .data import Pokedex

async def pokemon_autocomplete(interaction: discord.Interaction, current: str):
    names = Pokedex.get_base_names()
    matches = [name for name in names if current.lower() in name.lower()]
    return [app_commands.Choice(name=m, value=m) for m in matches[:25]]

class Cobblemon(commands.GroupCog, name="cobblemon"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="fetchcobblemon", hidden=True)
    @commands.is_owner()
    async def fetch_cobblemon(self, ctx):
        embed, _ = await FetchCobblemon.fetch_cobblemon_data()
        await ctx.send(embed=embed)

    @app_commands.command(name="list", description="List all Pokémon in Cobblemon")
    async def list_pokemon(self, interaction: discord.Interaction):
        embed, ephemeral = await List.cobblemon_list()
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @app_commands.command(name="types", description="List all Pokémon of a specific type")
    @app_commands.describe(type="Choose a Pokémon type")
    @app_commands.choices(type=[app_commands.Choice(name=name.capitalize(), value=name)for name in TYPE_EMOJIS.keys()])
    async def types(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        pages, ephemeral = await List.cobblemon_types(type.value)

        if not pages:
            return await interaction.response.send_message("No data found.", ephemeral=True)

        if len(pages) == 1:
            await interaction.response.send_message(embed=pages[0], ephemeral=ephemeral)
        else:
            paginator = ButtonPaginator(pages=pages, author_id=interaction.user.id)
            await paginator.start(interaction)

    @app_commands.command(name="moves", description="Show all available moves for a Pokémon")
    @app_commands.describe(pokemon="Choose a Pokémon")
    @app_commands.autocomplete(pokemon=pokemon_autocomplete)
    async def moves(self, interaction: discord.Interaction, pokemon: str):
        pages, ephemeral = await Pokedex.moves(pokemon)

        if not pages:
            return await interaction.response.send_message("No data found.", ephemeral=True)

        if len(pages) == 1:
            await interaction.response.send_message(embed=pages[0], ephemeral=ephemeral)
        else:
            paginator = ButtonPaginator(pages=pages, author_id=interaction.user.id)
            await paginator.start(interaction)

    @app_commands.command(name="spawns", description="Show spawn locations for a Pokémon")
    @app_commands.describe(pokemon="Choose a Pokémon")
    @app_commands.autocomplete(pokemon=pokemon_autocomplete)
    async def spawns(self, interaction: discord.Interaction, pokemon: str):
        pages, ephemeral = await Pokedex.cobblemon_spawns(pokemon)

        if not pages:
            return await interaction.response.send_message("No data found.", ephemeral=True)

        if len(pages) == 1:
            await interaction.response.send_message(embed=pages[0], ephemeral=ephemeral)
        else:
            paginator = ButtonPaginator(pages=pages, author_id=interaction.user.id)
            await paginator.start(interaction)

    @app_commands.command(name="pokedex", description="Look up a Pokémon by name")
    @app_commands.describe(pokemon="Choose a Pokémon")
    @app_commands.autocomplete(pokemon=pokemon_autocomplete)
    async def pokedex(self, interaction: discord.Interaction, pokemon: str):
        pages, ephemeral = await Pokedex.cobblemon_pokedex(pokemon)

        if not pages:
            return await interaction.response.send_message("Pokémon not found.", ephemeral=True)

        paginator = ButtonPaginator(pages=pages, author_id=interaction.user.id)
        await paginator.start(interaction, ephemeral=ephemeral)

async def setup(bot: commands.Bot):
    await bot.add_cog(Cobblemon(bot))
