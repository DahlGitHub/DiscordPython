import discord
from discord import app_commands
from discord.ext import commands
from typing import List
import aiohttp
import asyncio

import config
from utils.league import QUEUE_ID
import utils.emotes as emotes

class Matches(commands.GroupCog, name="matches", description="Riot Account Matches commands"):
    """
    Get Riot Account LoL Matches from X queue within Y timeframe.
    """

    def __init__(self, bot):
        self.bot = bot


    async def queueID_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        queueids = [id[0] for id in QUEUE_ID.items()]
        return [
            app_commands.Choice(name=queueid, value=queueid)
            for queueid in queueids if current.lower() in queueid.lower()
        ]

    @app_commands.command(name="matches", description="Get LoL matches for a Riot Account")
    @app_commands.describe(
        # summoner_name='The name of the summoner',
        # summoner_tag='The tag of the summoner without "#" (e.g., "pants")',
        # region='The region of the summoner (e.g., "na1", "euw1")',
        queue='The queue type (e.g., "RANKED_SOLO_5x5")',
        # start_time='ddmmyy - E.G. 010200 (1st Feb 2000) From 16th June 2021 and later',
        # end_time='ddmmyy - E.G. 010200 (1st Feb 2000) From 16th June 2021 and later',
        # limit='The number of matches to retrieve (default is 10, max is 100)',
    )
    @app_commands.autocomplete(queue=queueID_autocomplete)
    async def matches(
        self,
        interaction: discord.Interaction,
        # summoner_name: str,
        # summoner_tag: str,
        # region: str = 'euw1',
        queue: str = 'RANKED_SOLO_5x5',
        # start_time: str = '160621',
        # end_time: str = '160621',
        # limit: int = 10
    ):
        # Validate the limit
        # if limit < 1 or limit > 100:
        #     await interaction.response.send_message("Limit must be between 1 and 100.", ephemeral=True)
        #     return

        # Fetch matches from Riot API (placeholder URL)
        # url = f"https://{region}.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_name}?queue={queue}&beginTime={start_time}&endTime={end_time}&endIndex={limit}"
        
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(url, headers={"X-Riot-Token": config.RIOT_API_KEY}) as response:
        #         if response.status != 200:
        #             await interaction.response.send_message("Failed to fetch matches. Please check the summoner name and region.", ephemeral=True)
        #             return
                
        #         data = await response.json()
        #         matches = data.get("matches", [])
                
        #         if not matches:
        #             await interaction.response.send_message("No matches found for the specified criteria.", ephemeral=True)
        #             return
                
        #         # Format the response
        #         match_list = "\n".join([f"Match ID: {match['gameId']}, Champion: {match['champion']}" for match in matches[:limit]])
                
        #         embed = discord.Embed(title=f"Matches for {summoner_name}", description=match_list, color=config.Color_Default)
        #         await interaction.response.send_message(embed=embed)
        print(f"Matches command called with queue: {queue}")

    @commands.command(name="match", description="Test command for matches")
    async def match(self, ctx):
        print(queueid := [(key, value['queueid']) for key, value in QUEUE_ID.items()])
        await ctx.message.add_reaction('✅')

    
    @commands.command(name="matches", description="Get LoL matches for a Riot Account")
    async def matches(
        self,
        interaction: discord.Interaction,
        summoner_name: str,
        summoner_tag: str,
        queue: str = 'RANKED_SOLO_5x5',
        start_time: str = '160621',
        # end_time: str = '160621',
        # region: str = 'euw1',
        limit: int = 10
    ):

        # Validate the limit
        if limit < 1 or limit > 100:
            await interaction.response.send_message("Limit must be between 1 and 100.", ephemeral=True)
            return
        dbquery = "SELECT puuid FROM riot_accounts WHERE username = $1 AND tag = $2"
        dbresult = await self.bot.db.fetchrow(dbquery, username.lower(), tag.lower())

        if dbresult:
            puuid = dbresult['puuid']
        else:
            await interaction.response.send_message(f"No account found for the specified username and tag, please add account with command /save_lol_account.", ephemeral=True)
            return
        # Fetch matches from Riot API (placeholder URL)
        time_now = discord.utils.utcnow().timestamp()
        url = f"https://{config.RIOT_API_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={start_time}&endTime={time_now}&queue={queue}&type=ranked&start=0&count={limit}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"X-Riot-Token": config.RIOT_API_KEY}) as response:
                if response.status != 200:
                    await interaction.response.send_message("Failed to fetch matches. Please check the summoner name and region.", ephemeral=True)
                    return

                data = await response.json()
                matches = data.get("matches", [])

                if not matches:
                    await interaction.response.send_message("No matches found for the specified criteria.", ephemeral=True)
                    return

                # Format the response
                match_list = "\n".join([f"Match ID: {match['gameId']}, Champion: {match['champion']}" for match in matches[:limit]])

                embed = discord.Embed(title=f"Matches for {summoner_name}", description=match_list, color=config.Color_Default)
                await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Matches(bot))