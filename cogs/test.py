import discord
from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command()
    async def settest(self, ctx, key: str, *, value: str):
        await self.db.execute(
            """
            INSERT INTO test_data (key, value) VALUES ($1, $2)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
            """, key, value)
        await ctx.send(f"Set `{key}` = `{value}`")

    @commands.command()
    async def gettest(self, ctx, key: str):
        row = await self.db.fetchrow("SELECT value FROM test_data WHERE key = $1", key)
        if row:
            await ctx.send(f"Value for `{key}`: `{row['value']}`")
        else:
            await ctx.send(f"No value found for `{key}`.")

async def setup(bot):
    db = bot.db
    await bot.add_cog(Test(bot, db))
