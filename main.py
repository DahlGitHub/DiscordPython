import platform
import asyncio
import importlib
import sys
import humanize

import discord
from discord.ext import commands
from datetime import datetime, timezone
import config
import utils.emotes as emotes
from data.asqlite import SQLite
import jishaku
from pathlib import Path

from utils.extensions import ExtensionManager
from utils.commandsync import sync_commands
from utils.presence import restore_presence

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(config.PREFIX), 
    help_command=None, 
    case_insensitive=True,
    application_id=config.DISCORD_APPLICATION_ID,
    intents=discord.Intents.all())

TOKEN = config.DISCORD_TOKEN
jishaku.Flags.NO_UNDERSCORE = True
jishaku.Flags.NO_DM_TRACEBACK = True

sqlite = SQLite()
bot.sqlite = sqlite
extension_manager = ExtensionManager(bot, sqlite)

bot.remove_command('help')
bot.launch_time = datetime.now(timezone.utc)
recent_cog = None
commands_synced = False
sync_lock = asyncio.Lock()

"""
The following functions below are meant to simple run the bot, and load all the extensions.

"""

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


async def manage_extension(ctx, action: str, extension: str):
    name = extension.strip().lower()
    root = Path(__file__).resolve().parent
    available = sorted(
        '.'.join(file.relative_to(root).with_suffix('').parts)
        for file in (root / 'cogs').rglob('*.py') if file.name != '__init__.py'
    )
    saved = await extension_manager.saved()
    if name == 'all':
        targets = available if action == 'load' else list(dict.fromkeys([*saved, *ctx.bot.extensions]))
        if action == 'reload':
            targets = list(ctx.bot.extensions)
    else:
        name = name if name.startswith('cogs.') or name == 'jishaku' else f'cogs.{name}'
        known = list(dict.fromkeys([*available, *saved, *ctx.bot.extensions]))
        targets = [name] if name in known else [ext for ext in known if ext.startswith(name + '.')]
        if action == 'reload':
            targets = [ext for ext in targets if ext in ctx.bot.extensions]
    if action == 'unload':
        targets = list(reversed(targets))
    results = []
    changed = False
    for target in targets:
        try:
            await extension_manager.apply(action, target)
            changed = True
            results.append(f'{emotes.Check} `{target}`: {action} successful.')
        except Exception as exc:
            results.append(f'{emotes.Cross} `{target}`: {exc}')
    if changed:
        failed = await sync_all_commands()
        results.append('Slash commands synced.' if not failed else
                       'Some slash commands could not sync. Check the console or retry with sync.')
    if not results:
        results = ['No matching extensions found.']
    text = '\n'.join(results)
    while text:
        split = text.rfind('\n', 0, 3800) if len(text) > 3800 else len(text)
        if split <= 0:
            split = min(len(text), 3800)
        embed = discord.Embed(description=text[:split], color=config.Color_Default)
        embed.set_author(name='Cogs Handler:', icon_url=ctx.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
        text = text[split:].lstrip('\n')
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
    global recent_cog
    await manage_extension(ctx, "reload", extension)
    recent_cog = extension

@bot.command(name="r", hidden=True)
@commands.is_owner()
async def reload_recent(ctx):
    global recent_cog
    if not recent_cog:
        await ctx.send("No cog was found")
        return
    await manage_extension(ctx, "reload", recent_cog)

@bot.command(hidden=True)
@commands.is_owner()
async def extensions(ctx):
    loaded = set(bot.extensions.keys())

    cogs_path = Path("cogs")

    available = set()

    for file in cogs_path.rglob("*.py"):
        if file.name == "__init__.py":
            continue

        extension = ".".join(file.with_suffix("").parts)
        available.add(extension)

    unloaded = available - loaded

    if loaded:
        loaded_desc = "\n".join(
            f"- `{ext}`"
            for ext in sorted(loaded)
        )
    else:
        loaded_desc = "None."

    if unloaded:
        unloaded_desc = "\n".join(
            f"- `{ext}`"
            for ext in sorted(unloaded)
        )
    else:
        unloaded_desc = "None."

    embed = discord.Embed(
        description=(
            f"**Loaded extensions:**\n"
            f"{loaded_desc}\n\n"
            f"**Unloaded extensions:**\n"
            f"{unloaded_desc}"
        ),
        color=config.Color_Default
    )

    embed.set_author(
        name="Cogs Handler:",
        icon_url=bot.user.display_avatar.url
    )

    await ctx.send(embed=embed)
    await ctx.message.delete()

"""
Printing out status and versions upon start, notifying the owner the program is online.
"""
@bot.event
async def on_ready():
    global commands_synced
    await restore_presence(bot)
    if not commands_synced:
        commands_synced = True
        await sync_all_commands()
    
    print(f'Total cogs loaded: {len(bot.cogs)}')
    print(f'Total commands loaded: {len(bot.commands)}')
    print(f'Total slash commands loaded: {len(bot.tree.get_commands())}')
    print(f'Status: {bot.user} is online, {datetime.now()}.')
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")

async def sync_all_commands():
    failed = 0
    async with sync_lock:
        for guild in bot.guilds:
            try:
                synced = await sync_commands(bot, guild)
                print(f'Synced {len(synced)} slash commands for guild {guild.id}.')
            except Exception as exc:
                failed += 1
                print(f'Failed to sync slash commands for guild {guild.id}: {exc}')
    return failed


@bot.event
async def on_guild_join(guild):
    async with sync_lock:
        try:
            await sync_commands(bot, guild)
        except Exception as exc:
            print(f'Failed to sync slash commands for guild {guild.id}: {exc}')


async def cogs():
    """Restore only extensions explicitly enabled through the owner commands."""
    for extension in await extension_manager.saved():
        try:
            await bot.load_extension(extension)
            print(f'Loaded saved extension: {extension}')
        except Exception as exc:
            print(f'Failed to load saved extension {extension}: {exc}')


async def main():
    try:
        await sqlite.connect()
        await cogs()
        await bot.start(TOKEN)
    finally:
        await sqlite.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutdown the bot 🔴")
        sys.exit(0)
