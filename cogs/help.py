import discord
from discord.ext import commands

import config

class Help(commands.Cog):
    """
    Gives a list of all the commands.    
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *params):
        """
        Simply put, shows this function.
        """
        if not params:
            try:
                owner = ctx.guild.get_member(713481442331590747).mention
            except AttributeError:
                owner = "Adrian#4030"

            embed = discord.Embed(description=f'Use `.h <module>` to gain more information about that module ', color=discord.Colour(config.Color_Bot))
            embed.set_author(name="Help", icon_url=self.bot.user.display_avatar)

            cogs_desc = ''
            for cog in self.bot.cogs:
                if cog == "MessageListener" or cog == "Help":
                    continue
                cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

            embed.add_field(name='Modules', value=cogs_desc, inline=False)

            commands_desc = ''
            for command in self.bot.walk_commands():

                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            if commands_desc:
                embed.add_field(name='Misc', value=commands_desc, inline=False)

        elif len(params) == 1:

            for cog in self.bot.cogs:

                if cog.lower() == params[0].lower():

                    embed = discord.Embed(title=f'{cog} - commands', description=self.bot.cogs[cog].__doc__, color=discord.Colour(config.Color_Bot))
                    embed.set_author(name=f"Help {cog}", icon_url=self.bot.user.display_avatar)
                    for command in self.bot.get_cog(cog).get_commands():
              
                        if not command.hidden:
                            embed.add_field(name=f".{command.name}", value=command.help, inline=False)
                    break

        await ctx.send(embed = embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
    print('Help is loaded.')