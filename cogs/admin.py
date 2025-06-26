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
        ctx.bot.get_command(cmd).enabled = False
        embed = discord.Embed(description=f'{config.Status_Dnd} **{cmd}** has been disabled.', color=discord.Colour(config.Color_Bot))
        embed.set_author(name='Command Disabled:', icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def enable(self, ctx, cmd):
        """
        Enables a given cmd from the help list.
        """
        ctx.bot.get_command(cmd).enabled = True
        embed = discord.Embed(description=f'{config.Status_Online} **{cmd}** has been enabled.', color=discord.Colour(config.Color_Bot))
        embed.set_author(name='Command Enabled:', icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """
        Shut downs the bot.
        """
        embed = discord.Embed(description=f'{config.Status_Offline} Signing off.', color=discord.Colour(config.Color_Bot))
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

    # ------------ Slash command sync commands --------------

    @commands.command(name="globalsync")
    @commands.is_owner()
    async def globalsync(self, ctx):
        """
        Syncs slash commands globally (can take up to an hour to propagate).
        """
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"🔄 Globally synced {len(synced)} commands.")

    @commands.command(name="localsync")
    @commands.has_permissions(administrator=True)
    async def localsync(self, ctx):
        """
        Syncs slash commands for the current guild (instant update).
        """
        guild = ctx.guild
        synced = await ctx.bot.tree.sync(guild=guild)
        await ctx.send(f"🔄 Locally synced {len(synced)} commands for guild `{guild.name}`.")

    

async def setup(bot):
    await bot.add_cog(Admin(bot))
    print('Admin is loaded.')
