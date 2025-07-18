import asyncpg
import config
from pathlib import Path

SCHEMA_PATH = Path("data/schema.sql")

class Database:
    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            dsn=config.DATABASE_URL,
            min_size=1,
            max_size=10,
            max_inactive_connection_lifetime=300,
            timeout=5
        )
        async with self.pool.acquire() as conn:
            await self._create_tables(conn)

    async def close(self) -> None:
        if self.pool and not self.pool._closed:
            await self.pool.close()
            self.pool = None

    async def _create_tables(self, conn: asyncpg.Connection) -> None:
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
        for stmt in statements:
            await conn.execute(stmt)

    async def _conn(self) -> asyncpg.Connection:
        if not self.pool:
            raise RuntimeError("Database has not been awaited.")
        return await self.pool.acquire()

    async def execute(self, query: str, *args):
        return await self.pool.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        return await self.pool.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        return await self.pool.fetch(query, *args)
    
    async def fetchval(self, query: str, *args):
        return await self.pool.fetchval(query, *args)

