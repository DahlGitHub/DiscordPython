import asyncio
import logging
import math

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


log = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.tree_on_error

    def cog_unload(self):
        tree = self.bot.tree
        if tree.on_error == self.tree_on_error:
            tree.on_error = self._old_tree_error

    def get_error_message(self, error, command=None):
        name = getattr(command, "qualified_name", "unknown")
        bot_errors = (commands.BotMissingPermissions, app_commands.BotMissingPermissions,
                      commands.BotMissingRole, commands.BotMissingAnyRole)
        if isinstance(error, (*bot_errors, discord.HTTPException, discord.RateLimited,
                              aiohttp.ClientError, asyncio.TimeoutError, app_commands.CommandSignatureMismatch)):
            log.warning("Command %s failed (%s)", name, type(error).__name__)

        if isinstance(error, bot_errors):
            return "A bot permission or role check failed. Please let the bot owner know."
        elif isinstance(error, (commands.MissingPermissions, app_commands.MissingPermissions)):
            permissions = ", ".join(
                "Manage Server" if name == "manage_guild" else name.replace("_", " ").title()
                for name in error.missing_permissions
            )
            return f"You need these permissions to use this command: {permissions}."
        elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole,
                                app_commands.MissingRole, app_commands.MissingAnyRole)):
            return "You don't have the role required to use this command."
        elif isinstance(error, commands.NotOwner):
            return "Only the bot owner can use this command."
        elif isinstance(error, (commands.NoPrivateMessage, app_commands.NoPrivateMessage)):
            return "Use this command in a server, rather than in a direct message."
        elif isinstance(error, commands.PrivateMessageOnly):
            return "Use this command in a direct message to the bot."
        elif isinstance(error, commands.NSFWChannelRequired):
            return "This command can only be used in an age-restricted channel."
        elif isinstance(error, (commands.CommandOnCooldown, app_commands.CommandOnCooldown, discord.RateLimited)):
            seconds = max(1, math.ceil(error.retry_after))
            return f"Try again in {seconds} {'second' if seconds == 1 else 'seconds'}."
        elif isinstance(error, commands.MaxConcurrencyReached):
            return "This command is already running. Please wait for it to finish."
        elif isinstance(error, commands.DisabledCommand):
            return "This command is currently disabled."
        elif isinstance(error, commands.MissingRequiredAttachment):
            return f"Attach a file for `{error.param.displayed_name or error.param.name}`."
        elif isinstance(error, commands.MissingRequiredArgument):
            return f"You're missing the `{error.param.displayed_name or error.param.name}` argument."
        elif isinstance(error, commands.TooManyArguments):
            return "You provided too many arguments. Check the command's usage."
        elif isinstance(error, commands.UserInputError):
            return "Some arguments are invalid. Check the command's usage."
        elif isinstance(error, app_commands.TransformerError):
            return "One of the command options is invalid. Check your input and try again."
        elif isinstance(error, app_commands.CommandSignatureMismatch):
            return "This command needs updating. Please ask a server administrator to sync commands."
        elif isinstance(error, (commands.CheckFailure, app_commands.CheckFailure)):
            return "You can't use this command here."
        elif isinstance(error, discord.Forbidden):
            return "Discord blocked that action. Check the target and my role position."
        elif isinstance(error, discord.NotFound):
            return "That message or resource could not be found. It may have been deleted."
        elif isinstance(error, discord.HTTPException):
            return "Discord could not complete that action. Please try again later."
        elif isinstance(error, asyncio.TimeoutError):
            return "The service took too long to respond. Please try again later."
        elif isinstance(error, aiohttp.ClientError):
            return "The service is currently unavailable. Please try again later."

        log.error("Command %s failed", name, exc_info=(type(error), error, error.__traceback__))
        return "Something went wrong while running this command. Please try again later."

    async def send_error(self, interaction, message):
        if interaction.is_expired():
            log.warning("Could not report command error: interaction %s expired", interaction.id)
            return
        kwargs = {"ephemeral": True, "allowed_mentions": discord.AllowedMentions.none()}
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message[:1900], **kwargs)
            else:
                try:
                    await interaction.response.send_message(message[:1900], **kwargs)
                except discord.InteractionResponded:
                    await interaction.followup.send(message[:1900], **kwargs)
        except (discord.HTTPException, discord.RateLimited, aiohttp.ClientError, asyncio.TimeoutError) as error:
            log.warning(
                "Could not send command error for interaction %s (%s)", interaction.id, type(error).__name__
            )

    async def tree_on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if interaction.extras.get("command_error_handled"):
            return
        while hasattr(error, "original"):
            error = error.original
        if isinstance(error, app_commands.CommandNotFound):
            return
        command = interaction.command
        has_local_handler = getattr(command, "_has_any_error_handlers", lambda: False)
        if has_local_handler() and interaction.response.type in (
            discord.InteractionResponseType.channel_message, discord.InteractionResponseType.message_update,
        ):
            return
        interaction.extras["command_error_handled"] = True
        message = self.get_error_message(error, command)
        await self.send_error(interaction, message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.command and ctx.command.has_error_handler():
            return
        if ctx.cog and ctx.cog.has_error_handler():
            return
        while hasattr(error, "original"):
            error = error.original
        if isinstance(error, commands.CommandNotFound):
            return
        interaction = ctx.interaction
        if interaction and interaction.extras.get("command_error_handled"):
            return
        message = self.get_error_message(error, ctx.command)
        if isinstance(error, commands.UserInputError) and ctx.command:
            invocation = f"{ctx.clean_prefix}{ctx.command.qualified_name} {ctx.command.signature}".strip()
            message += f"\nUsage: `{invocation.replace('`', '')}`"
        if interaction:
            interaction.extras["command_error_handled"] = True
            await self.send_error(interaction, message)
            return
        try:
            await ctx.send(message[:1900], allowed_mentions=discord.AllowedMentions.none())
        except (discord.HTTPException, discord.RateLimited, aiohttp.ClientError, asyncio.TimeoutError) as send_error:
            log.warning(
                "Could not send command error in channel %s (%s)", ctx.channel.id, type(send_error).__name__
            )


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
