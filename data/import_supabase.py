"""Optional one-time import: python -m data.import_supabase (stop the bot first)."""

import asyncio
from datetime import date, datetime
import os

from dotenv import load_dotenv

from data.asqlite import SQLite


async def main():
    # Only this optional migration tool needs asyncpg.
    import asyncpg

    load_dotenv()
    dsn = os.getenv('database_url')
    if not dsn:
        raise RuntimeError('Set database_url in .env to import existing Supabase records.')
    source = await asyncpg.connect(dsn, timeout=15)
    target = SQLite()
    try:
        await target.connect()
        tables = await target.fetch(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
        # A failed import rolls back all imported rows. Existing local rows win.
        await target.execute('BEGIN')
        try:
            for table in tables:
                name = table['name']
                exists = await source.fetchval('SELECT to_regclass($1)', f'public.{name}')
                if exists is None:
                    continue
                rows = await source.fetch(f'SELECT * FROM "{name}"')
                columns = {row['name'] for row in await target.fetch(f'PRAGMA table_info("{name}")')}
                inserted = 0
                for row in rows:
                    fields = [field for field in row.keys() if field in columns]
                    values = [row[field].isoformat() if isinstance(row[field], (datetime, date))
                              else row[field] for field in fields]
                    quoted = ', '.join(f'"{field}"' for field in fields)
                    placeholders = ', '.join('?' for _ in fields)
                    inserted += await target.execute(
                        f'INSERT INTO "{name}" ({quoted}) VALUES ({placeholders}) ON CONFLICT DO NOTHING',
                        *values,
                    )
                print(f'{name}: imported {inserted} of {len(rows)} rows')
        except BaseException:
            await target.execute('ROLLBACK')
            raise
        else:
            await target.execute('COMMIT')
    finally:
        await target.close()
        await source.close()


if __name__ == '__main__':
    asyncio.run(main())
