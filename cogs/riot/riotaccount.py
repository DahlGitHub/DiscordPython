import discord
from discord import app_commands
from discord.ext import commands
from typing import List
import aiohttp
import asyncio

import config


# async def fruit_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
#     fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
#     return [
#         app_commands.Choice(name=fruit, value=fruit)
#         for fruit in fruits if current.lower() in fruit.lower()
#     ]


class RiotAccount(commands.GroupCog, name="riotaccount", description="RiotAccount commands"):
    """
    RiotAccount commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.LOL_RANK_TYPE = {
            "RANKED_SOLO_SR": "Ranked Solo/Duo",
            "RANKED_FLEX_SR": "Ranked Flex",
            "RANKED_TFT": "Ranked TFT",
            "RANKED_SOLO_5x5": "Ranked Solo",
        }


    @commands.command()
    async def roles1(self, ctx):
        """
        Get a list of all roles in the server.
        """
        roles = [role for role in ctx.guild.roles[1:]]

        embed = discord.Embed(description="   ".join([role.mention for role in roles]),
                              colour=discord.Colour(config.Color_Default))

        embed.set_author(name=f"{ctx.guild} Roles ({len(ctx.guild.roles) - 1})", icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    async def getPuuid (self, username: str, tag: str):
        
        dbquery = "SELECT puuid FROM riot_accounts WHERE username = $1 AND tag = $2"
        dbresult = await self.bot.db.fetchrow(dbquery, username.lower(), tag.lower())
        if dbresult:
            return (True, dbresult['puuid'])
        else:

            async with aiohttp.ClientSession() as session:
                url = f"https://{config.RIOT_API_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
                headers = {"X-Riot-Token": config.RIOT_API_KEY}
                try:
                    response = await session.get(url, headers=headers)
                    if response.status == 200:
                        data = await response.json()
                        # print(f"Response data: {data}")
                    else:
                        responseText = await response.text()
                        print(f"Failed to fetch data. Status code: {response.status}, Response: responseText, URL: {url}")
                        error_msg = f"Failed to fetch data. Status code: {response.status}, Response: responseText"
                        return (False, error_msg)

                except aiohttp.ClientError as e:
                    print(f"ClientError occurred: {e}")

                return( True, data['puuid'])

    @commands.command()
    async def bestgame(self, ctx):
        """
        Returns the best game ever.
        """
        msg = "Path of Exile is the best game ever, according to the developer of this bot."
        embed = discord.Embed(description=msg, colour=discord.Colour(config.Color_Default))
        embed.set_author(name=f"{ctx.guild}: Best Game", icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    async def fruits_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[
        app_commands.Choice[str]]:
        fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
        return [
            app_commands.Choice(name=fruit, value=fruit)
            for fruit in fruits if current.lower() in fruit.lower()
        ]

    @app_commands.command(name='testfetch', description='Test command for autocomplete in database')
    @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in config.GUILDS])
    @app_commands.describe(table='Test input for database')
    async def testfetch(self, interaction: discord.Interaction, table: str):
        """
        Test command to fetch data from the database.
        """
        try:
            query = f"SELECT * FROM {table}"
            response = await self.bot.db.fetch(query)
            if response:
                embed = discord.Embed(
                    description=f"✅ Fetched data from `{table}` database:\n{response}",
                    color=discord.Colour(config.Color_Default)
                )
            else:
                embed = discord.Embed(
                    description=f"❌ No data found in `{table}` database.",
                    color=discord.Colour(config.Color_Error)
                )

            embed.set_author(name="Database Query Result:", icon_url=interaction.guild.icon.url)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error executing testfetch command: {e}")
            embed = discord.Embed(
                description=f"❌ Failed to fetch data from `{table}` database:\n{e}",
                color=discord.Colour(config.Color_Error)
            )
            embed.set_author(name="Error:", icon_url=interaction.guild.icon.url)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name='fruits', description='Select your favourite fruit')
    @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in config.GUILDS])
    @app_commands.describe(fruit='Select your favourite fruit')
    @app_commands.autocomplete(fruit=fruits_autocomplete)
    async def fruits(self, interaction: discord.Interaction, fruit: str):
        await interaction.response.send_message(f'Your favourite fruit seems to be {fruit}')


    # @commands.command(name='my_account', description='Get your League of Legends account information')
    @app_commands.command(name='my_account', description='Get your League of Legends account information')
    @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in config.GUILDS])
    @app_commands.describe(username='Your Riot username', tag='Your Riot tag')
    async def my_account(self, interaction: discord.Interaction, username: str, tag: str):
        """
        Get your account information.
        """
        dbquery = "SELECT puuid FROM riot_accounts WHERE username = $1 AND tag = $2"
        dbresult = await self.bot.db.fetchrow(dbquery, username.lower(), tag.lower())

        if dbresult:
            puuid = dbresult['puuid']
        # else:
            # embed = discord.Embed(
            #     description=f"❌ No account found for `{username}#{tag}` in the database, please add it with command '~save_lol_account [username] [tag]' (without #).",
            #     color=discord.Colour(config.Color_Error)
            # )
            # embed.set_author(name="Error:", icon_url=interaction.guild.icon.url)
            # await interaction.response.send_message(embed=embed)
            # return
        
        async with aiohttp.ClientSession() as session:
            if not puuid:
                url = f"https://{config.RIOT_API_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
                headers = {"X-Riot-Token": config.RIOT_API_KEY}
                try:
                    response = await session.get(url, headers=headers)
                    if response.status == 200:
                        data = await response.json()
                        puuid = data['puuid']
                        # print(f"Response data: {data}")
                    else:
                        print(f"Failed to fetch account from riotgames. Status code: {response.status}, Response: {await response.text()}, URL: {url}")
                        await interaction.response.send_message(
                            f"❌ Failed to fetch account information for `{username}#{tag}`. Please check the username and tag."
                        )
                        return
                except aiohttp.ClientError as e:
                    print(f"ClientError occurred: {e}")

                # print(f"Fetching account information for {username}#{tag}... puuid:{puuid}")            

            try:
                response = await session.get(
                    f'https://{config.RIOT_API_SERVER_EUW}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}',
                    headers={'X-Riot-Token': config.RIOT_API_KEY}
                )
                if response.status == 200:
                    data = await response.json()
                    print(f"Response data for account info: {data}")
                else:
                    print(f"Failed to fetch ranked information. Status code: {response.status}, Response: {await response.text()}, URL: {url} ")

                    await interaction.response.send_message(
                        f"❌ Failed to fetch ranked information for `{username}#{tag}`. Please check the username and tag."
                    )
                    return
            except aiohttp.ClientError as e:
                print(f"ClientError occurred while fetching ranked info: {e}")
                await interaction.response.send_message(
                    f"❌ An error occurred while fetching ranked information for `{username}#{tag}`."
                )
                return

            embed = discord.Embed(
                title=f"{username}'s Account Information",
                description=f"{username}#{tag} has {data[0]['wins']} wins and {data[0]['losses']} losses in {self.LOL_RANK_TYPE[data[0]['queueType']]}.",
                color=discord.Colour(config.Color_Default)
            )
            await interaction.response.send_message(embed=embed)

    # @commands.command(name='save_lol_account', description='Save your League of Legends account information')
    @app_commands.command(name='save_lol_account', description='Save your League of Legends account information')
    @app_commands.describe(username='Your League of Legends username', tag='Your League of Legends tag')
    async def save_lol_account(self, interaction: discord.Interaction, username: str, tag: str):
        """
        Save your League of Legends account information.
        """
        async with aiohttp.ClientSession() as session:
            url = f"https://{config.RIOT_API_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
            headers = {"X-Riot-Token": config.RIOT_API_KEY}
            try:
                response = await session.get(url, headers=headers)
                if response.status == 200:
                    data = await response.json()
                    print(f"Response data: {data}")
                    puuid = data['puuid']
                else:
                    print(f"Failed to fetch data. Status code: {response.status}")

            except aiohttp.ClientError as e:
                print(f"ClientError occurred: {e}")

            print("Starting db insertion for account information...")
            try:
                dbquery = "INSERT INTO riot_accounts (username, tag, puuid, region) VALUES ($1, $2, $3, $4) ON CONFLICT (puuid) DO UPDATE SET username = $1, tag = $2, puuid = $3, last_updated = NOW()"
                dbresponse = await self.bot.db.execute(dbquery, username.lower(), tag.lower(), puuid, "euw")
                if dbresponse:
                    print(f"Database response: {dbresponse}")

                    embed = discord.Embed(
                        description=f"✅ Your League of Legends account `{username}#{tag}` has been saved successfully.",
                        color=discord.Colour(config.Color_Default)
                    )
                    embed.set_author(name="Account Saved:", icon_url=interaction.guild.icon.url)
                    await interaction.response.send_message(embed=embed)
                    # await ctx.message.delete()
                    return
            except Exception as e:
                print(f"Error inserting into database: {e}")

            embed = discord.Embed(
                description=f"❌ Failed to save your League of Legends account `{username}#{tag}` to the database.",
                color=discord.Colour(config.Color_Error)
            )
            embed.set_author(name="Error:", icon_url=interaction.guild.icon.url)
            await interaction.response.send_message(embed=embed)
            # await ctx.message.delete()

    @commands.command(name="fmatch")
    async def fmatch(self, ctx, username: str, tag: str, num_matches):
        """
        Test.
        """
        puuidResponse = await self.getPuuid(username, tag)
        if puuidResponse[0] == False:
            embed = discord.Embed(
                description=puuidResponse[1],
                color = discord.Color(config.Color_Error)
            )        
            embed.set_author(name=f"{ctx.guild}: Best Game", icon_url=ctx.guild.icon.url)
            await ctx.send(embed=embed)
            await ctx.message.delete()
            return
        
        embed = discord.Embed(
            description=f"Account {username}#{tag} found. Good job",
            color = discord.Color(config.Color_Default)
        )        
        embed.set_author(name=f"{ctx.guild}: Best Game", icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
        await ctx.message.delete()
    

async def setup(bot):
    await bot.add_cog(RiotAccount(bot))