import sys
import traceback
import discord
from discord.ext import commands
from utils.embedbuilder import EmbedBuilder
import config
from discord import app_commands, Interaction

# Just a generic error for all errors, until it can be handled more specifically.
class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.tree_on_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def tree_on_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        await interaction.response.send_message(error, ephemeral=False)
        print(f"An error occurred in a slash command: {error}")
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(error)
        print(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
