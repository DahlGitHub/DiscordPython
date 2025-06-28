import platform
import asyncio
import os
import importlib
import sys

import discord
from discord.ext import commands
from discord import app_commands
from utils.embedbuilder import EmbedBuilder
from data.database import Database

from datetime import datetime, timezone
from dotenv import load_dotenv
import humanize

import config
import utils.emotes as emotes

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(config.PREFIX), 
    help_command=None, 
    case_insensitive=True,
    application_id='1386471915597856940',
    intents=discord.Intents.all())

load_dotenv()
TOKEN = os.getenv('discord_token')

db = Database()
bot.db = db

bot.remove_command('help')
bot.launch_time = datetime.now(timezone.utc)

"""
The following functions below are meant to simple run the bot, and load all the extensions.

"""

async def cogs():
    """
    This code is executed whenever the main.py is launched, loading all the following /cogs/__.py files.
    """
    for filename in os.listdir("cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(filename)

# Utilizing discord.Embed in main.py to keep it seperate from custom EmbedBuilder.
@bot.command()
@commands.is_owner()
async def uptime(ctx):
    """
    Status for how long the bot has been online. 
    """
    uptime = datetime.now(timezone.utc) - bot.launch_time
    embed = discord.Embed(description=f"Bot has been online for: {humanize.precisedelta(uptime)}",color=config.Color_Default)
    embed.set_author(name="Uptime:", icon_url=bot.user.display_avatar.url)
    embed.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=embed)

@bot.command(hidden=True)
@commands.is_owner()
async def reloadutils(ctx, module_name: str):
    try:
        full_module = f"utils.{module_name.lower()}"
        if full_module in sys.modules:
            importlib.reload(sys.modules[full_module])
        else:
            importlib.import_module(full_module)
        embed = discord.Embed(
            description=f'{emotes.Check} `{module_name}` utility has been reloaded.', 
            color=config.Color_Default
        )
        embed.set_author(name="Utils Handler:", icon_url=bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            description=f"{emotes.Cross} Failed to reload utility `{module_name}`:\n{e}", 
            color=config.Color_Error
        )
        embed.set_author(name="Utils Handler:", icon_url=bot.user.display_avatar.url)
        await ctx.send(embed=embed)


async def manage_extension(ctx, action: str, extensions: str):
    extension = extensions.lower()
    try:
        method = getattr(ctx.bot, f"{action}_extension")
        await method(f'cogs.{extension}')
        embed = discord.Embed(description=f'{emotes.Check} `{extension.capitalize()}` extension has been {action}ed.', color=config.Color_Default)
        embed.set_author(name="Cogs Handler:", icon_url=bot.user.display_avatar.url)
        await ctx.send(embed=embed)
        await ctx.message.delete()
    except Exception as e:
        embed = discord.Embed(description=f"{emotes.Cross} Failed to {action} extension `{extension.capitalize()}`:\n{e}",color=config.Color_Error)
        embed.set_author(name="Cogs Handler:", icon_url=bot.user.display_avatar.url)
        await ctx.send(embed=embed)
        await ctx.message.delete()
        
@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension: str):
    await manage_extension(ctx, "load", extension)

@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension: str):
    await manage_extension(ctx, "unload", extension)

@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension: str):
    await manage_extension(ctx, "reload", extension)

@bot.command(hidden=True)
@commands.is_owner()
async def extensions(ctx):
    loaded = list(bot.extensions.keys())
    if not loaded:
        desc = "No extensions currently loaded."
    else:
        desc = "\n".join(f"- `{ext}`" for ext in loaded)
    embed = discord.Embed(description=f"**Loaded extensions:**\n{desc}", color=config.Color_Default)
    embed.set_author(name="Cogs Handler:", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)
    await ctx.message.delete()

"""
Printing out status and versions upon start, notifying the owner the program is online.
"""
@bot.event
async def on_ready():
    
    print(f'Status: {bot.user} is online, {datetime.now()}.')
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")

async def main():
    await db.connect()
    await cogs()
    await bot.start(TOKEN)

asyncio.run( main() )