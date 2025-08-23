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
    
    async def upload_matches(self, puuid: str, matches: List[dict]):
        """
        Upload matches to the database.
        """
        concat_matches = ''.join([f"('{puuid}', '{id}')," for id in matches]).rstrip(',')
        dbquery = f"INSERT INTO lol_match_id (puuid, match_id) VALUES {concat_matches} ON CONFLICT (puuid, match_id) DO NOTHING"
        print(f"DB Query: {dbquery}")
        
        try:
            return (True, await self.bot.db.execute(dbquery))
        except Exception as e:
            print(f"Error uploading matches: {e}")
            return (False, e)



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
        # Note: probaly puuid is needed instead of summoner name and tag
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


    @commands.command()
    # start_time 1755196260 = 14th aug 2025
    async def get_matches(self, ctx, username: str, tag: str, queueID: str = '900', start_time: str = '1755196260'):
        """
        Get recent matches for a League of Legends account after a point in time.
        """
        dbquery = "SELECT puuid FROM riot_accounts WHERE username = $1 AND tag = $2"
        dbresult = await self.bot.db.fetchrow(dbquery, username.lower(), tag.lower())        
        puuid = dbresult['puuid']

        if not dbresult:
            embed = discord.Embed(
                description=f"❌ No account found for `{username}#{tag}` in the database, please add it with command '~save_lol_account [username] [tag]' (without #).",
                color=discord.Colour(config.Color_Error)
            )
            embed.set_author(name="Error:", icon_url=ctx.guild.icon.url)
            await ctx.send(embed=embed)
            return
        
        # puuid, start_time, end_time, queue_type (normal, ranked, tourney...), start_index, end_index
        async with aiohttp.ClientSession() as session:
            url = f"https://{config.RIOT_API_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={start_time}&queue={queueID}&type=normal"
            headers = {"X-Riot-Token": config.RIOT_API_KEY}
            try:
                response = await session.get(url, headers=headers)
                # print(f"response: {await response.json()}")
                if response.status != 200:
                    embed = discord.Embed(
                        # description=f"❌ Failed to fetch matches with code '{response.status.status_code}' and message: '{response.status.message}'",
                        description=f"❌ Failed to fetch matches with code & message'{response.status}'",
                        color=discord.Colour(config.Color_Error)
                    )
                    embed.set_author(name="Error:", icon_url=ctx.guild.icon.url)
                    await ctx.send(embed=embed)
                    return
                
                data = await response.json()
                print(f"response data: {data}")
                matches = data

                if not matches:
                    embed = discord.Embed(
                        description="❌ No matches found for the specified criteria.",
                        color=discord.Colour(config.Color_Error)
                    )
                    embed.set_author(name="Error:", icon_url=ctx.guild.icon.url)
                    await ctx.send(embed=embed)
                    return

                upload_result = await self.upload_matches(puuid, matches)
                if not upload_result[0]: #------------- Upload could still fail, this just a naive check --------------------------
                    embed = discord.Embed(
                        description=f"❌ Failed to upload matches for `{username}#{tag}` to the database. Error: {upload_result[1]}",
                        color=discord.Colour(config.Color_Error)
                    )
                    embed.set_author(name="Error:", icon_url=ctx.guild.icon.url)
                    await ctx.send(embed=embed)
                    return

                embed = discord.Embed(
                    description=f"Recent matches for `{username}#{tag}` in `{queueID}` after {start_time}: \n" + "\n".join(matches),
                    color=discord.Colour(config.Color_Default)

                )
                embed.set_author(name="Success:", icon_url=ctx.guild.icon.url)
                await ctx.send(embed=embed)

            except aiohttp.ClientError as e:
                embed = discord.Embed(
                    description=f"❌ Failed to fetch matches: {str(e)}",
                    color=discord.Colour(config.Color_Error)
                )
                embed.set_author(name="Error:", icon_url=ctx.guild.icon.url)
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Matches(bot))