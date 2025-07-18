import discord
from discord.ext import commands

import config
import utils.emotes as emotes

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
        embed = discord.Embed(description=f'{emotes.Status_Dnd} **{cmd}** has been disabled.', color=discord.Colour(config.Color_Default))
        embed.set_author(name='Command Disabled:', icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def enable(self, ctx, cmd):
        """
        Enables a given cmd from the help list.
        """
        ctx.bot.get_command(cmd).enabled = True
        embed = discord.Embed(description=f'{emotes.Status_Online} **{cmd}** has been enabled.', color=discord.Colour(config.Color_Default))
        embed.set_author(name='Command Enabled:', icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setstatus(self, ctx, activity_type: str, *, message: str):
        
        activity_map = {
            "playing": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
            "streaming": discord.ActivityType.streaming
        }

        if activity_type not in activity_map:
            return await ctx.send("Need an activity type.")
        
        activity = discord.Activity(type=activity_map[activity_type.lower()], name=message)
        await self.bot.change_presence(activity=activity)
        await ctx.send(f"✅ Status set to: {activity_type.title()} {message}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """
        Shut downs the bot.
        """
        embed = discord.Embed(description=f'{emotes.Status_Offline} Signing off.', color=discord.Colour(config.Color_Default))
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

    @commands.command(name="sync")
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx):
        """
        Syncs slash commands for the current guild (instant update).
        """
        tree = self.bot.tree
        guild = ctx.guild
        tree.copy_global_to(guild=guild)
        synced = await tree.sync(guild=guild)
        await ctx.send(f"🔄 Locally synced {len(synced)} commands for guild `{guild.name}`.")

    @commands.command(name="localremove")
    @commands.is_owner()
    @commands.has_permissions(administrator=True)
    async def syncremove(self, ctx):
        """
        Removes all locally synced slash commands for the current guild.
        """
        guild = ctx.guild
        ctx.bot.tree.clear_commands(guild=guild)
        await ctx.send(f"🗑️ Locally removed all slash commands for guild `{guild.name}`.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
