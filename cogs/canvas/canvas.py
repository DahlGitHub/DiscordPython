import discord
from discord.ext import commands
from discord import app_commands

import config
from utils.embedbuilder import EmbedBuilder
import utils.emotes as emotes

class Canvas(commands.Cog):
    """
    Canvas commands, general configuration for the bot. 
    """
    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    @commands.is_owner()
    async def canvas(self, ctx):
        """
        Canvas command to interact with the bot.
        """
        embed = discord.Embed(
            title="Canvas Command",
            description="This is a placeholder for the Canvas command.",
            color=config.Color_Default

        )
        embed.set_author(name="Canvas", icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="Info", value=emotes.CS2, inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="canvas", description="new sync")
    async def canvas_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Canvas Command",
            description="This is a placeholder for the Canvas command.",
            color=config.Color_Default
        )
        embed.set_author(name="Canvas", icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="Info", value=emotes.CS2, inline=False)
        await interaction.response.send_message(embed=embed)

    @commands.command()
    async def CustomEmbed(self, ctx):
        """
        Alias for the canvas command.
        """
        embed = EmbedBuilder(
            title="Canvas Command",
            description="This is a placeholder for the Canvas command.",
            bot=self.bot,
            ctx=ctx,
        ).author(name="Canvas", icon="bot")
        await ctx.send(embed=embed)

    @app_commands.command(name="customembed", description="Alias for the canvas command")
    @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in config.GUILDS])
    async def CustomEmbedSlash(self, interaction: discord.Interaction):
        """
        Alias for the canvas command.
        """
        embed = EmbedBuilder(
            title="Canvas Command",
            description="This is a placeholder for the Canvas command.",
            bot=self.bot,
            interaction=interaction,
        ).author(name="Canvas", icon="bot")
        await interaction.response.send_message(embed=embed)

    @commands.command()
    async def DefaultEmbed(self, ctx):
        """
        Alias for the canvas command.
        """
        embed = discord.Embed(title="Canvas Command",
            description="This is a placeholder for the Canvas command.",
            color=config.Color_Default,
            type="rich",
            url="https://example.com" , # Example URL, can be replaced with a real one
            timestamp=ctx.message.created_at  # Use the message timestamp
        )
        embed.set_author(name="Canvas", icon_url=self.bot.user.display_avatar.url)
        embed.set_author(name="bot", icon_url=self.bot.user.display_avatar.url)
        embed.set_author(name="Server", icon_url=ctx.guild.icon.url)
        embed.set_author(name="user", icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Info", value="Info", inline=False)
        embed.set_footer(text="This is a footer", icon_url=self.bot.user.display_avatar.url )
        embed.set_thumbnail(url="https://example.com/thumbnail.png")
        embed.set_image(url="https://example.com/image.png")

        await ctx.send(embed=embed)

    @commands.command()
    async def getAvatar(self, ctx):
        user = ctx.author
        guild = ctx.guild
        bot_user = self.bot.user

        msg = (
            f"**User Avatars**\n"
            f"`ctx.author.display_avatar.url:` {user.display_avatar}\n"
            f"`ctx.author.avatar:` {user.avatar.url if user.avatar else 'None'}\n"
            f"`ctx.author.default_avatar.url:` {user.default_avatar}\n\n"

            f"**Guild Info**\n"
            f"`ctx.guild.icon:` {guild.icon.url if guild.icon else 'None'}\n"
            f"`ctx.guild.banner:` {guild.banner.url if guild.banner else 'None'}\n"
            f"`ctx.guild.splash:` {guild.splash.url if guild.splash else 'None'}\n\n"

            f"**Bot Info**\n"
            f"`self.bot.user.display_avatar.url:` {bot_user.display_avatar}\n"
            f"`self.bot.user.avatar:` {bot_user.avatar.url if bot_user.avatar else 'None'}\n"
        )
        embed = discord.Embed(
            title="Attributes",
            description= msg,
            color=config.Color_Default
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def jskcheck(self, ctx):
        cmds = [cmd.qualified_name for cmd in self.bot.commands if "py" in cmd.qualified_name or "jishaku" in cmd.qualified_name]
        await ctx.send(f"Loaded commands: {cmds or 'None'}")


async def setup(bot):
    await bot.add_cog(Canvas(bot))