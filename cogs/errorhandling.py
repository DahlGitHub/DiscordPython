import sys
import traceback
import discord
from discord.ext import commands
from utils.embedbuilder import EmbedBuilder
import config  # Your constants file

# Icons by severity
ERROR_ICON = "https://cdn.discordapp.com/attachments/1040802472496746616/1050213752680747128/discord-322.png"
WARN_ICON = "https://cdn.discordapp.com/attachments/1040802472496746616/1050213415202865153/discord-321.png"
FATAL_ICON = "https://cdn.discordapp.com/attachments/1040802472496746616/1050213526943322182/discord-32.png"

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_user_error(self, ctx, message: str, title: str = "Error", icon_url: str = ERROR_ICON):
        embed = EmbedBuilder(description=message, ctx=ctx)\
            .author(name=title, icon=icon_url)\
            .theme("error")\
            .timestamp()\
            .build()
        await ctx.send(embed=embed)

    async def log_unexpected(self, ctx, error):
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        log_channel_id = getattr(config, "Error_Log_Channel_ID", None)
        if log_channel_id:
            channel = self.bot.get_channel(log_channel_id)
            if channel:
                tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
                truncated_tb = tb[-1900:] if len(tb) > 1900 else tb
                await channel.send(
                    f"💥 **Unhandled Error in `{ctx.command}` by {ctx.author}:**\n```py\n{truncated_tb}```"
                )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        # === Ignored ===
        if isinstance(error, commands.CommandNotFound):
            return

        # === User-Facing Errors ===
        if isinstance(error, commands.DisabledCommand):
            await self.send_user_error(ctx, f"`{ctx.command}` is currently disabled.", icon_url=ERROR_ICON)

        elif isinstance(error, commands.NoPrivateMessage):
            await self.send_user_error(ctx, "This command cannot be used in private messages.", icon_url=ERROR_ICON)

        elif isinstance(error, commands.MissingPermissions):
            await self.send_user_error(ctx, "You're missing the required permissions to run this command.", icon_url=ERROR_ICON)

        elif isinstance(error, commands.BotMissingPermissions):
            await self.send_user_error(ctx, "I’m missing the required permissions to perform this action.", icon_url=ERROR_ICON)

        elif isinstance(error, commands.CheckFailure):
            await self.send_user_error(ctx, "You don’t have access to this command.", icon_url=ERROR_ICON)

        elif isinstance(error, commands.UserInputError):
            await self.send_user_error(ctx, f"Invalid input. Try `.help {ctx.command}` for usage.", icon_url=WARN_ICON)

        # === Unexpected Error ===
        else:
            await self.send_user_error(ctx, "An unexpected error occurred. It has been logged.", icon_url=FATAL_ICON)
            await self.log_unexpected(ctx, error)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
    print("✅ ErrorHandler cog loaded.")
