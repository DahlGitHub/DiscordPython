import asyncio
from pathlib import Path

import asqlite


class SQLite:
    """Shared local storage for all bot features."""

    def __init__(self, path="data/database.db"):
        self.path = Path(path)
        self.connection = None
        self.lock = asyncio.Lock()

    async def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = await asqlite.connect(str(self.path))
        async with self.connection.cursor() as cursor:
            await cursor.executescript(
                Path("data/sqlite_schema.sql").read_text(encoding="utf-8")
            )

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def execute(self, query, *args):
        async with self.lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, args)
                return cursor.get_cursor().rowcount

    async def fetch(self, query, *args):
        async with self.lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, args)
                return await cursor.fetchall()

    async def fetchrow(self, query, *args):
        async with self.lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, args)
                return await cursor.fetchone()

    async def fetchval(self, query, *args):
        row = await self.fetchrow(query, *args)
        return row[0] if row is not None else None
