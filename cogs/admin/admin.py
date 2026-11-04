import discord
from datetime import datetime, timezone
import humanize
from discord.ext import commands

import config
import utils.emotes as emotes
from utils.commandsync import sync_commands
from utils.presence import save_presence

class Admin(commands.Cog):
    """
    Admin commands, general configuration for the bot. 
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def status(self, ctx):
        """Show basic bot health and background check schedules."""
        embed = discord.Embed(title='Bot status', color=config.Color_Default)
        uptime = datetime.now(timezone.utc) - self.bot.launch_time
        embed.add_field(name='Uptime', value=humanize.precisedelta(uptime))
        embed.add_field(name='Latency', value=f'{self.bot.latency * 1000:.0f} ms')
        embed.add_field(name='Extensions', value=str(len(self.bot.extensions)))
        try:
            await self.bot.sqlite.fetchval('SELECT 1')
        except Exception:
            database = 'Unavailable'
        else:
            database = 'Connected'
        embed.add_field(name='Database', value=database)

        checks = []
        for cog_name, loop_name, label in (
            ('SteamNotifications', 'watcher', 'Steam wishlists'),
            ('SteamPromotions', 'free_checker', 'Steam free games'),
            ('SteamPromotions', 'weekend_checker', 'Steam free weekends'),
            ('Patches', 'patch_checker', 'League patches'),
        ):
            cog = self.bot.get_cog(cog_name)
            if cog is None:
                state = 'Not loaded'
            else:
                loop = getattr(cog, loop_name)
                if loop.failed():
                    state = 'Failed'
                elif loop.is_running():
                    state = 'Running'
                    if loop.next_iteration:
                        state += f' (next {discord.utils.format_dt(loop.next_iteration, "R")})'
                else:
                    state = 'Stopped'
            checks.append(f'**{label}:** {state}')
        embed.add_field(name='Background checks', value='\n'.join(checks), inline=False)
        await ctx.send(embed=embed)

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
    @commands.max_concurrency(1, wait=True)
    async def setstatus(self, ctx, activity_type: str, *, message: str = ''):
        """Set a persistent activity or online status; use clear to remove activity."""
        try:
            await save_presence(self.bot, activity_type, message)
        except ValueError as exc:
            await ctx.send(str(exc))
            return
        await ctx.send('Status saved. It will stay until you update it.', allowed_mentions=discord.AllowedMentions.none())

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
        guild = ctx.guild
        synced = await sync_commands(self.bot, guild)
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
