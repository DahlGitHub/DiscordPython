"""Extension lifecycle with persistent startup preferences."""

import asyncio


class ExtensionManager:
    def __init__(self, bot, storage):
        self.bot = bot
        self.storage = storage
        self.lock = asyncio.Lock()

    async def saved(self):
        rows = await self.storage.fetch('SELECT extension FROM enabled_extensions ORDER BY rowid')
        return [row['extension'] for row in rows]

    async def apply(self, action, extension):
        """Save successful changes; restore runtime state if saving fails."""
        async with self.lock:
            if action == 'reload':
                await self.bot.reload_extension(extension)
                return
            if action == 'load':
                already_loaded = extension in self.bot.extensions
                if not already_loaded:
                    await self.bot.load_extension(extension)
                try:
                    await self.storage.execute(
                        'INSERT OR IGNORE INTO enabled_extensions (extension) VALUES (?)', extension
                    )
                except Exception:
                    if not already_loaded:
                        await self.bot.unload_extension(extension)
                    raise
            elif action == 'unload':
                was_loaded = extension in self.bot.extensions
                if was_loaded:
                    await self.bot.unload_extension(extension)
                try:
                    await self.storage.execute(
                        'DELETE FROM enabled_extensions WHERE extension = ?', extension
                    )
                except Exception:
                    if was_loaded:
                        await self.bot.load_extension(extension)
                    raise
            else:
                raise ValueError(f'Unknown extension action: {action}')
