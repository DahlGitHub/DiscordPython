import discord
from discord.ext import commands

import config


class Canvas(commands.Cog):
    """
    Canvas commands, general configuration for the bot. 
    """
    def __init__(self, bot):
        self.bot = bot



async def setup(bot):
    await bot.add_cog(Canvas(bot))
    print('Canvas is loaded.')