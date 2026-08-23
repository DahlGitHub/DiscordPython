import re

import discord
from discord import app_commands
from discord.ext import commands

import config


FIXER_CHOICES = [
    app_commands.Choice(name="Instagram", value="instagram"),
    app_commands.Choice(name="Reddit", value="reddit"),
    app_commands.Choice(name="Twitter", value="twitter"),
]


class Embedfix(commands.GroupCog, name="embedfix"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.fixers = {
            "instagram": {
                "pattern": re.compile(r"https?://(?:www\.)?instagram\.com/\S+"),
                "replace_pattern": re.compile(r"(https?://(?:www\.)?)instagram\.com"),
                "default_replacement": "https://ddinstagram.com",
                "example": "https://www.instagram.com/p/example/",
            },
            "reddit": {
                "pattern": re.compile(r"https?://(?:www\.)?reddit\.com/\S+"),
                "replace_pattern": re.compile(r"(https?://(?:www\.)?)reddit\.com"),
                "default_replacement": "https://rxddit.com",
                "example": "https://www.reddit.com/r/example/comments/example/",
            },
            "twitter": {
                "pattern": re.compile(r"https?://(?:www\.)?twitter\.com/\S+"),
                "replace_pattern": re.compile(r"(https?://(?:www\.)?)twitter\.com"),
                "default_replacement": "https://vxtwitter.com",
                "example": "https://twitter.com/example/status/123456789",
            },
        }

        self.active_channels = {
            fixer: set()
            for fixer in self.fixers
        }

        self.custom_replacements = {}

    def get_replacement(self, guild_id: int, fixer: str) -> str:
        guild_data = self.custom_replacements.get(guild_id, {})

        return guild_data.get(
            fixer,
            self.fixers[fixer]["default_replacement"]
        )

    def get_fixed_example(self, guild_id: int, fixer: str) -> str:
        data = self.fixers[fixer]
        replacement = self.get_replacement(guild_id, fixer)

        return data["replace_pattern"].sub(
            replacement,
            data["example"]
        )

    def is_enabled(self, channel_id: int, fixer: str) -> bool:
        return channel_id in self.active_channels[fixer]

    def is_any_enabled(self, channel_id: int) -> bool:
        return any(
            self.is_enabled(channel_id, fixer)
            for fixer in self.fixers
        )

    @app_commands.command(
        name="list",
        description="List current embedfix settings."
    )
    async def list_fixers(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Embedfix",
            color=config.Color_Default
        )

        for fixer, data in self.fixers.items():
            status = (
                "ON"
                if self.is_enabled(interaction.channel_id, fixer)
                else "OFF"
            )

            replacement = self.get_replacement(
                interaction.guild_id,
                fixer
            )

            fixed_example = self.get_fixed_example(
                interaction.guild_id,
                fixer
            )

            embed.add_field(
                name=f"{fixer.capitalize()} — {status}",
                value=(
                    f"**Current:** `{replacement}`\n"
                    f"**Example:** `{data['example']}`\n"
                    f"**Result:** `{fixed_example}`"
                ),
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @app_commands.command(
        name="toggle",
        description="Toggle a specific embedfix fixer."
    )
    @app_commands.describe(fixer="Choose a fixer")
    @app_commands.choices(fixer=FIXER_CHOICES)
    async def toggle(
        self,
        interaction: discord.Interaction,
        fixer: app_commands.Choice[str]
    ):
        channel_id = interaction.channel_id
        fixer_name = fixer.value

        if self.is_enabled(channel_id, fixer_name):
            self.active_channels[fixer_name].remove(channel_id)
            status = "disabled"
        else:
            self.active_channels[fixer_name].add(channel_id)
            status = "enabled"

        await interaction.response.send_message(
            f"✅ {fixer.name} embedfix {status} in this channel.",
            ephemeral=True
        )

    @app_commands.command(
        name="all",
        description="Toggle all embedfix fixers in this channel."
    )
    async def toggle_all(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        enable = not self.is_any_enabled(channel_id)

        for fixer in self.fixers:
            if enable:
                self.active_channels[fixer].add(channel_id)
            else:
                self.active_channels[fixer].discard(channel_id)

        status = "enabled" if enable else "disabled"

        await interaction.response.send_message(
            f"✅ All embed fixes {status} in this channel.",
            ephemeral=True
        )

    @app_commands.command(
        name="setfixer",
        description="Set a custom replacement URL for a fixer."
    )
    @app_commands.describe(
        fixer="Choose a fixer",
        replacement_url="Custom replacement URL"
    )
    @app_commands.choices(fixer=FIXER_CHOICES)
    async def setfixer(
        self,
        interaction: discord.Interaction,
        fixer: app_commands.Choice[str],
        replacement_url: str
    ):
        guild_id = interaction.guild_id

        self.custom_replacements.setdefault(
            guild_id,
            {}
        )[fixer.value] = replacement_url

        await interaction.response.send_message(
            (
                f"✅ {fixer.name} replacement set to:\n"
                f"`{replacement_url}`"
            ),
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        original = message.content
        content = original

        for fixer, data in self.fixers.items():
            if not self.is_enabled(message.channel.id, fixer):
                continue

            if not data["pattern"].search(content):
                continue

            replacement = self.get_replacement(
                message.guild.id,
                fixer
            )

            content = data["replace_pattern"].sub(
                replacement,
                content
            )

        if content == original:
            return

        try:
            await message.delete()

            await message.channel.send(
                f"{message.author.mention} reposted:\n{content}"
            )

        except discord.Forbidden:
            print("Missing permissions to delete or send messages.")

        except discord.HTTPException as e:
            print(f"Failed to delete/send message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Embedfix(bot))