import platform
import time

import discord
from discord.ext import commands
from discord import app_commands

import config

"""
A module to provide most of the general information regarding the application,
"""

class Info(commands.Cog):
    """
    General information for bot, user and server.
    """
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        Ping the bot, return it's responses.
        """
        websocket = round(self.bot.latency*1000, 2)
        start = time.perf_counter()
        if websocket < 70:
            health = config.Status_Online
        elif 60 < websocket < 150:
            health = config.Status_Idle
        else:
            health = config.Status_Dnd
        embed = discord.Embed(color=0x000000, description=f"{health} | Websocket Latency **{websocket}** ms!", colour=discord.Color(config.Color_Bot))
        embed.set_author(name='Ping', icon_url=self.bot.user.display_avatar)
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)
        if duration < 145:
            health = config.Status_Online
        elif 145 < duration < 250:
            health = config.Status_Idle
        else:
            health = config.Status_Dnd
        embed.description += f"\n{health} | Response Time **{duration}** ms!"
        await message.edit(embed=embed)

    @commands.command()
    async def user(self, ctx , member: discord.Member = None):
        """
        Get most of the basic info related to a user, related to the server then globally.
        """
        member = ctx.author if not member else member
        local_emojis = []
        if member == ctx.guild.owner:
            local_emojis.append(config.Server_Owner)
        if ctx.channel.permissions_for(member).ban_members:
            local_emojis.append(config.Server_Mod)
        if member in ctx.guild.premium_subscribers:
            local_emojis.append(config.Server_Boost)
        emojies = {emoji for emoji in local_emojis[0:]}
        roles = [role for role in member.roles[0:]]

        sl = {
            discord.Status.online: config.Status_Online,
            discord.Status.offline: config.Status_Offline,
            discord.Status.idle: config.Status_Idle,
            discord.Status.dnd: config.Status_Dnd
            }

        embed = discord.Embed(description="", color=discord.Colour(config.Color_Bot), timestamp=ctx.message.created_at)

        embed.set_author(name=member, icon_url=member.display_avatar)
        embed.set_thumbnail(url=member.display_avatar)

        embed.add_field(name='Nickname:', value=member.display_name)
        embed.add_field(name="\u200B", value=" ".join([emoji for emoji in emojies]))
        embed.add_field(name='Discord ID:', value=member.id, inline=False)

        embed.add_field(name='Status:', value=f'{sl[member.web_status]} **Web Status**\n{sl[member.desktop_status]} **Desktop Status**\n{sl[member.mobile_status]} **Mobile Status**')
        embed.add_field(name='Activity:', value=f"{str(member.activity.type).split('.')[-1].title() if member.activity else 'N/A'} {member.activity.name if member.activity else ''}", inline=True)
        embed.add_field(name='Created Account:', value=member.created_at.strftime('%a, %#d %B %Y'), inline=False)
        embed.add_field(name='Joined Server:', value=member.joined_at.strftime('%a, %#d %B %Y'), inline=False)
    
        embed.add_field(name=f'Roles: ({len(roles)})', value=" ".join([role.mention for role in roles]))
        
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def bot(self, ctx):
        """
        Get most of the basic info related to the bot.
        """
        try:
            owner = ctx.guild.get_member(713481442331590747).mention
        except AttributeError:
            owner = "AdrianD#8008"

        embed = discord.Embed(description="", color=discord.Colour(config.Color_Bot))

        embed.set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar)
        embed.set_thumbnail(url=self.bot.user.display_avatar)

        embed.add_field(name='Made by:' , value=owner)
        embed.add_field(name='Application:', value=(
            f"Servers: {len(self.bot.guilds)}\n"
            f"Users:{len(self.bot.users)}\n"
            f"Members: {sum([i.member_count for i in self.bot.guilds])}\n\n"
            f"Commands: {len(list(self.bot.walk_commands()))}\n"
            ), inline=False)
        embed.add_field(name='Versions', value=f"Discord.py: {discord.__version__}\nPython: {platform.python_version()}", inline=False)
        
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def server(self, ctx):
        """
        Get most of the basic info of the server.
        """
        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        text_channels = [text_channel for text_channel in ctx.guild.text_channels]
        voice_channels = [voice_channel for voice_channel in ctx.guild.voice_channels]
        categories = [category for category in ctx.guild.categories]

        embed = discord.Embed(
            colour=discord.Colour(config.Color_Bot),
            description=(
                f'{config.Server_Owner} **{ctx.guild.owner}** | {ctx.guild.owner.mention} \n'
                f'\n{config.Server_Emoji} **{len(ctx.guild.emojis)}** | {config.Server_Roles} **{len(ctx.guild.roles)}**\n'
                f'\n{config.Server_Category} **{len(categories)}** | {config.Channel_Text} **{len(text_channels)}** | {config.Channel_Voice} **{len(voice_channels)}**\n'
                f'\n{config.Server_Member} **{len(list(filter(lambda m: not m.bot, ctx.guild.members)))}** | {config.Server_Bot} **{len(list(filter(lambda m: m.bot, ctx.guild.members)))}**\n'
                f'\n{config.Status_Online} **{statuses[0]}**\n{config.Status_Idle} **{statuses[1]}**\n{config.Status_Dnd} **{statuses[2]}**\n{config.Status_Offline} **{statuses[3]}**')
                )
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(name='Created', value=(ctx.guild.created_at.strftime("%a, %d %B %Y")),inline=False)
        embed.set_author(name=f"{ctx.guild}", icon_url=ctx.guild.icon.url)
        
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def roles(self, ctx):
        """
        Get a list of all roles in the server.
        """
        roles = [role for role in ctx.guild.roles[1:]]
        
        embed = discord.Embed(description="   ".join([role.mention for role in roles]), colour=discord.Colour(config.Color_Bot))
        embed.set_author(name=f"{ctx.guild} Roles ({len(ctx.guild.roles)-1})", icon_url=ctx.guild.icon.url)
       
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def emotes(self, ctx):
        """
        Get a list of all the emotes in the server.
        """
        emojis = " ".join(map(str, ctx.guild.emojis))

        embed = discord.Embed(description=f'{emojis}', colour=discord.Colour(config.Color_Bot))
        embed.set_author(name=f"{ctx.guild} Emotes ({len(ctx.guild.emojis)})", icon_url=ctx.guild.icon.url)
        
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def channels(self, ctx, member: discord.Member = None):
        """
        Get a list of all the channels in the server.
        """
        embed = discord.Embed(colour=config.Color_Info)
        embed.set_author(icon_url=ctx.guild.icon.url,name=f"{ctx.guild} Channels ({len(ctx.guild.channels)-len(ctx.guild.categories)})")
        for c in ctx.guild.categories:
            x = []
            for i in c.channels:
                if isinstance(i, discord.TextChannel):
                    if i.is_nsfw():
                        channel = config.Channel_Nsfw
                    elif str(i.type) == "news":
                        channel = config.Channel_News
                    else:
                        if i.overwrites_for(ctx.guild.default_role).read_messages is False:
                            channel = config.Channel_Lock
                        else:
                            channel = config.Channel_Text
                    x.append(f"{channel} {i.name}")
                elif isinstance(i, discord.VoiceChannel):
                    if i.overwrites_for(ctx.guild.default_role).read_messages is False:
                        channel = config.Channel_Voice_Lock
                    else:
                        channel = config.Channel_Voice
                    x.append(f"{channel} {i.name}")
                else:
                    pass
            embed.add_field(name=f"{c}", value='\u200b' + "\n".join(x), inline=False)
        y = [b for b in ctx.guild.categories]
        chl = []
        for o in ctx.guild.channels:
            if o.category or o in y:
                pass
            else:
                if isinstance(o, discord.TextChannel):
                    if o.is_nsfw():
                        channel = config.Channel_Nsfw
                    elif str(o.type) == "news":
                        channel = config.Channel_News
                    else:
                        if o.overwrites_for(ctx.guild.default_role).read_messages is False:
                            channel = config.Channel_Lock
                        else:
                            channel = config.Channel_Text
                    chl.append(f"{channel} {o.name}")
                elif isinstance(o, discord.VoiceChannel):
                    if o.overwrites_for(ctx.guild.default_role).read_messages is False:
                        channel = config.Channel_Voice_Lock
                    else:
                        channel = config.Channel_Voice
                    chl.append(f"{channel} {o.name}")
                else:
                    pass
        embed.description = "\n".join(chl)
        
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """
        Get the avatar image of the given user.
        """
        member = ctx.author if not member else member

        embed = discord.Embed(color=discord.Colour(config.Color_Bot))
        embed.set_author(name=f"{member.display_name}#{member.discriminator}", icon_url=member.display_avatar)
        embed.set_image(url=member.display_avatar)
        
        await ctx.send(embed=embed)
        await ctx.message.delete()

    """
    @commands.hybrid_command(
        name="help",
        description="List all commands the bot has loaded."
    )
    async def help(self, context: Context) -> None:
        prefix = "."
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=0x9C84EF)
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            data = []
            for command in commands:
                description = command.description.partition('\n')[0]
                data.append(f"{prefix}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(name=i.capitalize(),
                            value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)
    """

async def setup(bot):
    await bot.add_cog(Info(bot))
    print('Info is loaded.')