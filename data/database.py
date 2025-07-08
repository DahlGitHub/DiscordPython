import asyncpg
import config

class Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        self.conn = await asyncpg.connect(config.DATABASE_URL)
        await self._create_tables()

    async def _create_tables(self):
        with open("data/schema.sql", "r") as f:
            schema_sql = f.read()
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        for stmt in statements:
            await self.conn.execute(stmt)

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def execute(self, query: str, *args):
        """Execute any query that doesn't return rows."""
        return await self.conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch a single row."""
        return await self.conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows."""
        return await self.conn.fetch(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch a single value."""
        return await self.conn.fetchval(query, *args)

