import discord
from discord.ext import commands
from discord import app_commands
import re
import config

class Embedfix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.fixers = {
            'instagram': {
                'pattern': re.compile(r'https?://(?:www\.)?instagram\.com/\S+'),
                'replace_pattern': re.compile(r'(https?://(?:www\.)?)instagram\.com'),
                'default_replacement': 'https://ddinstagram.com',
            },
            'reddit': {
                'pattern': re.compile(r'https?://(?:www\.)?reddit\.com/\S+'),
                'replace_pattern': re.compile(r'(https?://(?:www\.)?)reddit\.com'),
                'default_replacement': 'https://rxddit.com',
            },
            'twitter': {
                'pattern': re.compile(r'https?://(?:www\.)?twitter\.com/\S+'),
                'replace_pattern': re.compile(r'(https?://(?:www\.)?)twitter\.com'),
                'default_replacement': 'https://vxtwitter.com',
            },
        }
        self.active_channels = {fixer: set() for fixer in self.fixers}
        self.custom_replacements = {}

    def _get_replacement_url(self, guild_id, fixer_name):
        guild_data = self.custom_replacements.get(guild_id, {})
        return guild_data.get(fixer_name, self.fixers[fixer_name]['default_replacement'])

    def is_any_active(self, channel_id):
        return any(channel_id in chans for chans in self.active_channels.values())

    async def _toggle_fixer(self, interaction: discord.Interaction, fixer_name: str):
        channel_id = interaction.channel_id
        if channel_id in self.active_channels[fixer_name]:
            self.active_channels[fixer_name].remove(channel_id)
            await interaction.response.send_message(f"✅ {fixer_name.capitalize()} embedfix disabled in this channel.", ephemeral=True)
        else:
            self.active_channels[fixer_name].add(channel_id)
            await interaction.response.send_message(f"✅ {fixer_name.capitalize()} embedfix enabled in this channel.", ephemeral=True)

    @app_commands.command(name="list", description="List current embedfix toggles and replacement URLs.")
    async def list(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        guild_id = interaction.guild_id
        lines = []
        for fixer_name in self.fixers:
            status = "ON" if channel_id in self.active_channels[fixer_name] else "OFF"
            replacement = self._get_replacement_url(guild_id, fixer_name)
            lines.append(f"**{fixer_name.capitalize()}**: {status} (replacement URL: {replacement})")
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @app_commands.command(name="all", description="Toggle all embedfix fixers on or off in this channel.")
    async def all(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        if self.is_any_active(channel_id):
            for fixer in self.active_channels:
                self.active_channels[fixer].discard(channel_id)
            await interaction.response.send_message("✅ All embed fixes disabled in this channel.", ephemeral=True)
        else:
            for fixer in self.active_channels:
                self.active_channels[fixer].add(channel_id)
            await interaction.response.send_message("✅ All embed fixes enabled in this channel.", ephemeral=True)

    @app_commands.command(name="toggle", description="Toggle a specific embedfix fixer on or off in this channel.")
    @app_commands.describe(fixer_name="Name of the fixer (instagram, reddit, twitter)")
    async def toggle(self, interaction: discord.Interaction, fixer_name: str):
        fixer_name = fixer_name.lower()
        if fixer_name not in self.fixers:
            await interaction.response.send_message(f"❌ Fixer '{fixer_name}' not found. Available fixers: {', '.join(self.fixers.keys())}", ephemeral=True)
            return
        await self._toggle_fixer(interaction, fixer_name)

    @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in config.GUILDS])  # Replace with your actual guild IDs
    @app_commands.command(name="setfixer", description="Set a custom replacement URL for a fixer in this guild.")
    @app_commands.describe(fixer_name="Name of the fixer", replacement_url="Custom replacement URL")
    async def setfixer(self, interaction: discord.Interaction, fixer_name: str, replacement_url: str):
        fixer_name = fixer_name.lower()
        if fixer_name not in self.fixers:
            await interaction.response.send_message(f"❌ Fixer '{fixer_name}' not found. Available fixers: {', '.join(self.fixers.keys())}", ephemeral=True)
            return
        guild_id = interaction.guild_id
        if guild_id not in self.custom_replacements:
            self.custom_replacements[guild_id] = {}
        self.custom_replacements[guild_id][fixer_name] = replacement_url
        await interaction.response.send_message(f"✅ Custom replacement URL for {fixer_name} set to: {replacement_url}", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            return

        original_content = message.content
        new_content = original_content
        changed = False

        for fixer_name, data in self.fixers.items():
            if channel_id in self.active_channels[fixer_name]:
                if data['pattern'].search(new_content):
                    replacement_url = self._get_replacement_url(guild_id, fixer_name)
                    new_content = data['replace_pattern'].sub(replacement_url, new_content)
                    changed = True

        if changed and new_content != original_content:
            try:
                await message.delete()
                await message.channel.send(f"{message.author.mention} reposted:\n{new_content}")
            except discord.Forbidden:
                print("Missing permissions to delete or send messages.")
            except discord.HTTPException as e:
                print(f"Failed to delete/send message: {e}")

async def setup(bot):
    await bot.add_cog(Embedfix(bot))
