import ast
from pathlib import Path
import unittest

from data.asqlite import SQLite


class MigrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = SQLite(':memory:')
        await self.db.connect()
        self.addAsyncCleanup(self.db.close)

    async def test_migrated_queries_prepare_against_local_schema(self):
        # Prepare every static migrated query to catch SQL dialect, table, column,
        # and repeated-parameter errors without calling external service APIs.
        for folder in ('bloons', 'canvas', 'riot', 'utils', 'admin'):
            for path in (Path('cogs') / folder).glob('*.py'):
                for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                        continue
                    if node.func.attr not in ('execute', 'fetch', 'fetchrow', 'fetchval'):
                        continue
                    if not node.args or not isinstance(node.args[0], ast.Constant):
                        continue
                    query = node.args[0].value
                    if not isinstance(query, str):
                        continue
                    with self.subTest(file=str(path), query=query):
                        await self.db.fetch('EXPLAIN ' + query, *([None] * (len(node.args) - 1)))

    async def test_identity_scalar_and_repeated_parameters(self):
        await self.db.execute('INSERT INTO todo (user_id, message) VALUES (?1, ?2)', 123, 'Test')
        self.assertEqual(await self.db.fetchval('SELECT COUNT(*) FROM todo'), 1)
        self.assertEqual(await self.db.fetchval('SELECT id FROM todo'), 1)
        self.assertIsNone(await self.db.fetchval('SELECT id FROM todo WHERE user_id = ?', 456))
        query = ('INSERT INTO riot_accounts (username, tag, puuid, region) VALUES (?1, ?2, ?3, ?4) '
                 'ON CONFLICT(puuid) DO UPDATE SET username = ?1, last_updated = CURRENT_TIMESTAMP')
        await self.db.execute(query, 'old', 'tag', 'puuid', 'euw')
        await self.db.execute(query, 'new', 'tag', 'puuid', 'euw')
        self.assertEqual(await self.db.fetchval('SELECT username FROM riot_accounts'), 'new')

    async def test_canvas_subscription_upsert(self):
        query = ('INSERT INTO canvas_subscriptions VALUES (?1, ?2, ?3) '
                 'ON CONFLICT(user_id, course_id) DO UPDATE SET channel_id = ?3')
        await self.db.execute(query, 1, 2, 3)
        await self.db.execute(query, 1, 2, 4)
        self.assertEqual(await self.db.fetchval('SELECT channel_id FROM canvas_subscriptions'), 4)
