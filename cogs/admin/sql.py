import discord
from discord.ext import commands
from utils.embedbuilder import EmbedBuilder
import config

class Sql(commands.Cog):
    """
    Sql commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sqltables(self, ctx):
        tables = await self.bot.db.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        table_names = [row['table_name'] for row in tables]
        if not table_names:
            await ctx.send("No tables were found.")
            return
        e = EmbedBuilder(description=f"Tables:\n`{', '.join(table_names)}`")
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sqlquery(self, ctx, *, query: str):
        """
        Run a SQL Query
        """
        try:
            rows = await self.bot.db.fetch(query)
            if not rows:
                await ctx.send("Query ran but no results")
                return
            output = ""
            for row in rows:
                line = str(dict(row)) + "\n"
                if len(output) + len(line) > 1900:  # Leave some room for Discord's 2000 char limit
                    output += "\n...truncated due to message size limit."
                    break
                output += line
            e = EmbedBuilder(description={output}).author(name="Query")
            await ctx.send(embed=e)

        except Exception as e:
            e = EmbedBuilder(description={e}).author(name="SQL Error:")
            await ctx.send(embed=e)
            await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Sql(bot))