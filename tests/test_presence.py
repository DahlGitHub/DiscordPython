import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

import discord

from data.asqlite import SQLite
from utils.presence import restore_presence, save_presence


class PresenceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'presence.db'
        self.db = SQLite(self.path)
        await self.db.connect()
        self.addAsyncCleanup(self.db.close)
        self.bot = SimpleNamespace(sqlite=self.db, change_presence=AsyncMock())

    async def test_restore_after_restart(self):
        await save_presence(self.bot, 'watching', 'the server')
        await self.db.close()
        await self.db.connect()
        self.bot.change_presence.reset_mock()
        await restore_presence(self.bot)
        kwargs = self.bot.change_presence.call_args.kwargs
        self.assertEqual(kwargs['status'], discord.Status.online)
        self.assertEqual(kwargs['activity'].type, discord.ActivityType.watching)
        self.assertEqual(kwargs['activity'].name, 'the server')

    async def test_availability_preserves_activity_and_clear_preserves_availability(self):
        await save_presence(self.bot, 'playing', 'a game')
        await save_presence(self.bot, 'idle', '')
        self.assertEqual(self.bot.change_presence.call_args.kwargs['activity'].name, 'a game')
        await save_presence(self.bot, 'clear', '')
        self.assertEqual(self.bot.change_presence.call_args.kwargs,
                         {'status': discord.Status.idle, 'activity': None})
        await save_presence(self.bot, 'watching', 'something else')
        self.assertEqual(self.bot.change_presence.call_args.kwargs['status'], discord.Status.idle)

    async def test_invalid_input_preserves_saved_status(self):
        await save_presence(self.bot, 'playing', 'a game')
        for kind, message in [('invalid', ''), ('playing', ''), ('watching', 'x' * 129),
                              ('streaming', 'no url'), ('idle', 'unexpected'), ('clear', 'unexpected')]:
            with self.subTest(kind=kind, message=message):
                with self.assertRaises(ValueError):
                    await save_presence(self.bot, kind, message)
        row = await self.db.fetchrow('SELECT * FROM bot_presence')
        self.assertEqual(row['message'], 'a game')

    async def test_streaming_url(self):
        await save_presence(self.bot, 'streaming', 'https://twitch.tv/example A stream')
        activity = self.bot.change_presence.call_args.kwargs['activity']
        self.assertEqual(activity.url, 'https://twitch.tv/example')
        self.assertEqual(activity.name, 'A stream')

    async def test_no_saved_status_leaves_default_presence(self):
        await restore_presence(self.bot)
        self.bot.change_presence.assert_not_awaited()
