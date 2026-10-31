"""Sync server commands without keeping stale copies in the command tree."""

import asyncio

sync_lock = asyncio.Lock()


async def sync_commands(bot, guild):
    async with sync_lock:
        tree = bot.tree
        commands = tree.get_commands(guild=guild)
        try:
            tree.copy_global_to(guild=guild)
            return await tree.sync(guild=guild)
        finally:
            tree.clear_commands(guild=guild)
            for command in commands:
                tree.add_command(command, guild=guild)
