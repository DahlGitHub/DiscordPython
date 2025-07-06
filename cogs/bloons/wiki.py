import discord
from discord.ext import commands
from discord import app_commands

class BloonsWiki(commands.GroupCog, name="bloonswiki"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    #Wiki did not sync when it was here, had to move to line 18? Will check out later.
#    subgroup = app_commands.Group(name='skyrim', description='description')
#    @subgroup.command(name="add")#/bloonswiki skyrim add
#    async def bloonswiki_wiki(self, interaction: discord.Interaction):
#        await interaction.response.send_message("Yes")

#    @subgroup.command(name="remove")#/bloonswiki skyrim remove
#    async def bloonswiki_wiki(self, interaction: discord.Interaction):
#        await interaction.response.send_message("Yes")

#    @app_commands.command(name="wiki") #/bloonswiki wiki
#    async def bloonswiki_wiki(self, interaction: discord.Interaction):
#        await interaction.response.send_message("Yes")

async def setup(bot: commands.Bot):
    await bot.add_cog(BloonsWiki(bot))
