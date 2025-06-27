import platform
import asyncio
import random
import os

import discord
from discord.ext import commands
from discord import app_commands
from utils.embedbuilder import EmbedBuilder

from datetime import datetime
from dotenv import load_dotenv
import humanize

import config

"""
Standard setup for a bot:
- Importing from config.py for prefix
- Importing from .env for secret token
- Removing the default 'help' command
- Enabling all default discord.Intents
    * No additional permissions or configurations needed.

- Enabling all privileged discord.Intents
    * GUILD_PRESENCES
    * GUILD_MEMBERS
    * MESSAGE_CONTENT
"""

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(config.PREFIX), 
    help_command=None, 
    case_insensitive=True,
    application_id='1386471915597856940',
    intents=discord.Intents.all())

load_dotenv()
bot.remove_command('help')
bot.launch_time = datetime.utcnow()
TOKEN = os.getenv('discord_token')

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

@bot.command()
@commands.is_owner()
async def uptime(ctx):
    """
    Status for how long the bot has been online. 
    """
    uptime = datetime.utcnow() - bot.launch_time
    embed = discord.Embed(description=f'Ive been awake for **{humanize.precisedelta(uptime, minimum_unit="minutes")}**.',color=0xA62019)
    embed.set_author(name='Uptime:', icon_url='https://cdn.discordapp.com/attachments/733659418486505672/738539741989044295/download_4.png')
    await ctx.send(embed=embed)


@bot.command(hidden=True)
# @commands.is_owner()
async def reload(ctx, extensions):
    extensions = extensions.lower()
    try:
        await bot.reload_extension(f'cogs.{extensions}')
        desc = f'🔄 **{extensions}** extension has been reloaded.'
        embed = EmbedBuilder(description=desc, color="success", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)
        await ctx.message.delete()
    except commands.ExtensionNotLoaded:
        embed = EmbedBuilder(description=f"❌ Extension `{extensions}` is not loaded.", color="error", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)
    except commands.ExtensionNotFound:
        embed = EmbedBuilder(description=f"❌ Extension `{extensions}` not found.", color="error", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)
    except Exception as e:
        embed = EmbedBuilder(description=f"❌ Failed to reload extension `{extensions}`:\n{e}", color="error", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)

@bot.command(hidden=True)
# @commands.is_owner()
async def load(ctx, extensions):
    extensions = extensions.lower()
    try:
        await bot.load_extension(f'cogs.{extensions}')
        desc = f'✅ **{extensions}** extension has been loaded.'
        embed = EmbedBuilder(description=desc, color="success", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)
        await ctx.message.delete()
    except commands.ExtensionAlreadyLoaded:
        embed = EmbedBuilder(description=f"❌ Extension `{extensions}` is already loaded.", color="warning", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)
    except commands.ExtensionNotFound:
        embed = EmbedBuilder(description=f"❌ Extension `{extensions}` not found.", color="error", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)
    except Exception as e:
        embed = EmbedBuilder(description=f"❌ Failed to load extension `{extensions}`:\n{e}", color="error", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)

@bot.command(hidden=True)
# @commands.is_owner()
async def unload(ctx, extensions):
    extensions = extensions.lower()
    try:
        await bot.unload_extension(f'cogs.{extensions}')
        desc = f'🛑 **{extensions}** extension has been unloaded.'
        embed = EmbedBuilder(description=desc, color="warning", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)
        await ctx.message.delete()
    except commands.ExtensionNotLoaded:
        embed = EmbedBuilder(description=f"❌ Extension `{extensions}` is not loaded.", color="error", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)
    except Exception as e:
        embed = EmbedBuilder(description=f"❌ Failed to unload extension `{extensions}`:\n{e}", color="error", ctx=ctx).author(name="Control Panel:", icon="server").build()
        await ctx.send(embed=embed)

@bot.command(hidden=True)
# @commands.is_owner()
async def extensions(ctx):
    loaded = list(bot.extensions.keys())
    if not loaded:
        desc = "No extensions currently loaded."
    else:
        desc = "\n".join(f"- `{ext}`" for ext in loaded)
    embed = EmbedBuilder(description=f"**Loaded extensions:**\n{desc}", color="info", ctx=ctx)\
        .author(name="Control Panel:", icon="server")\
        .build()
    await ctx.send(embed=embed)

"""
Printing out status and versions upon start, notifying the owner the program is online.
"""
@bot.event
async def on_ready():
    print(f'Status: {bot.user} is online, {datetime.now()}.')
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")

async def main():
    await cogs()
    await bot.start(TOKEN)

asyncio.run( main() )