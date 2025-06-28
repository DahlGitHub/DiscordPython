# Aqslite for Sqlite (Offline)
# Asyncpg for Postgres (Online)

# This file is not used in the current codebase, but serves as a template for Aqslite usage.
# The template provides a simple example of how to use Asqlite in Cogs, however having a dedicated connection manager is recommended.
import discord
from discord.ext import commands
import asqlite
import random

class Asqlite(commands.Cog):
    """
    A simple wrapper around asqlite for async SQLite operations.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/database.db"

    async def cog_load(self):
        await self.create_tables()

    async def _create_tables(self):
        async with asqlite.connect(self.db_path) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "CREATE TABLE IF NOT EXISTS leaderboard ("
                    "guild INTEGER, "
                    "user INTEGER, "
                    "level INTEGER, "
                    "xp INTEGER, "
                    "PRIMARY KEY (guild, user))"
                )
            await db.commit()

    @commands.command()
    async def leaderboard(self, ctx):
        """
        Get a list of the Top 10 users in the current guild.
        """
        async with asqlite.connect('/data/levels.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "SELECT level, xp, user "
                    "FROM leaderboard "
                    "WHERE guild = ? "
                    "ORDER BY level DESC, xp DESC LIMIT 10",
                    (ctx.guild.id,)
                    )
                leaderboard_data = await cursor.fetchall()
                if leaderboard_data:
                    nousers = discord.Embed(title="No users",color=discord.Colour(random.randint(0, 0xFFFFFF)))
                    embed = discord.Embed(color=discord.Colour(random.randint(0, 0xFFFFFF)))
                    embed.set_author(icon_url=ctx.guild.icon.url,name=f'Leaderboard - {ctx.guild}')
                    tablecount = 0
                    ranks = []
                    users = []
                    levels = []
                    for table in leaderboard_data:
                        user = ctx.guild.get_member(table[2])
                        tablecount += 1
                        ranks.append(f"#{tablecount}")
                        users.append(f"{user.mention}")
                        levels.append(f"{table[0]} - `{table[1]} xp`")
                    embed.add_field(name="Rank", value=f'\n'.join(ranks), inline=True)
                    embed.add_field(name="Name", value=f'\n'.join(users), inline=True)
                    embed.add_field(name="Level", value=f'\n'.join(levels), inline=True)
                            
                    await ctx.message.delete()
                    return await ctx.send(embed=embed)

                await ctx.message.delete()
            await db.commit()
            return await ctx.send(embed=nousers)

    async def setup(bot):
        await bot.add_cog(Asqlite(bot))
        print('Asqlite is loaded.')