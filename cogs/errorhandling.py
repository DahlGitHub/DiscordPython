""""
Copyright @ DahlGithub


Description:
This is a school project program for a Discord bot made by using an API wrapper for Discord written in Python.
Discord.py - https://github.com/Rapptz/discord.py

V. 1.0
"""

import traceback
import sys

import discord
from discord.ext import commands


class Errorhandling(commands.Cog):
    """
    A module to handle errors, notifies if a user upon error.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        This is triggered whenever an error is raised.
        
        It will run through the most basic errors, until it reaches the bottom in case something unexpected happend.
        Printing out the TraceBack
        """

        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(description=f'{ctx.command} has been disabled.')
            embed.set_author(icon_url="https://cdn.discordapp.com/attachments/1040802472496746616/1050213752680747128/discord-322.png",name=error)
            await ctx.send(embed=embed)
        
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(description="I don't have enough permissions to do this.")
            embed.set_author(icon_url="https://cdn.discordapp.com/attachments/1040802472496746616/1050213752680747128/discord-322.png",name=error)
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description="You are missing permissions.")
            embed.set_author(icon_url="https://cdn.discordapp.com/attachments/1040802472496746616/1050213752680747128/discord-322.png",name=error)
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.UserInputError):
            embed = discord.Embed(description=f"Invalid input, check `.help {ctx.command}`")
            embed.set_author(icon_url="https://cdn.discordapp.com/attachments/1040802472496746616/1050213415202865153/discord-321.png",name=error)
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                embed = discord.Embed(description="This cannot be used in PM's.")
                embed.set_author(icon_url="https://cdn.discordapp.com/attachments/1040802472496746616/1050213752680747128/discord-322.png",name=error)
                await ctx.send(embed=embed)
            except discord.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(description="You do not have permission to use this command.")
            embed.set_author(icon_url="https://cdn.discordapp.com/attachments/1040802472496746616/1050213752680747128/discord-322.png",name=error)
            await ctx.send(embed=embed)
            return

        else:
            embed = discord.Embed(description="Unexpected error, check console.")
            embed.set_author(icon_url="https://cdn.discordapp.com/attachments/1040802472496746616/1050213526943322182/discord-32.png",name=error)
            await ctx.send(embed=embed)
            print(file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    
async def setup(bot):
    await bot.add_cog(Errorhandling(bot))
    print('Errorhandling is loaded.') 