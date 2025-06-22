""""
Copyright @ DahlGithub


Description:
This is a school project program for a Discord bot made by using an API wrapper for Discord written in Python.
Discord.py - https://github.com/Rapptz/discord.py

V. 1.0
"""

import discord
from discord.ext import commands

import config


class Admin(commands.Cog):
    """
    Admin commands, general configuration for the bot. 
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def disable(self, ctx, cmd):
        """
        Disables a given cmd from the help list.
        """
        ctx.bot.get_command(cmd).enabled=False
        embed = discord.Embed(description=f'{config.Status_Dnd} **{cmd}** has been disabled.',color=discord.Colour(config.Color_Bot))
        embed.set_author(name='Command Disabled:',icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def enable(self, ctx, cmd):
        """
        Enables a given cmd from the help list.
        """
        ctx.bot.get_command(cmd).enabled=True
        embed = discord.Embed(description=f'{config.Status_Online} **{cmd}** has been enabled.',color=discord.Colour(config.Color_Bot))
        embed.set_author(name='Command Enabled:',icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """
        Shut downs the bot.
        """
        embed = discord.Embed(description=f'{config.Status_Offline} Signing off.',color=discord.Colour(config.Color_Bot))
        embed.set_author(name='Control Panel', icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
        await ctx.message.delete()
        await self.bot.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        """
        Makes bot leave server
        """
        await self.bot.get_guild(ctx.guild.id).leave()


async def setup(bot):
    await bot.add_cog(Admin(bot))
    print('Admin is loaded.')