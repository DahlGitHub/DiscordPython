import re
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

import config


# Match only the URL's domain, leaving its path and query unchanged.
URL_PATTERN = re.compile(r"https?://(?:www\.)?([a-z0-9.-]+)(?=[/?#\s<>]|$)", re.IGNORECASE)


def parse_domain(value):
    domain = value.strip().lower().removeprefix("https://").removeprefix("http://")
    domain = domain.removeprefix("www.").rstrip("/")
    pattern = r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}"
    if len(domain) > 253 or not re.fullmatch(pattern, domain):
        raise ValueError("Use a domain such as e.g. instagram.com")
    return domain


def convert_links(content, rules):
    replacements = {row["source"]: row["target"] for row in rules}

    def replace(match):
        target = replacements.get(match.group(1).lower())
        if target:
            return "https://" + target
        return match.group()

    return URL_PATTERN.sub(replace, content)


@app_commands.guild_only()
class Embedfix(commands.GroupCog, name="embedfix"):
    def __init__(self, bot):
        self.bot = bot

    async def rules(self):
        return await self.bot.sqlite.fetch(
            "SELECT name, source, target FROM embedfix_rules ORDER BY name"
        )

    async def fixer_autocomplete(self, interaction, current):
        rows = await self.rules()
        return [app_commands.Choice(name=row["name"], value=row["name"])
                for row in rows if current.lower() in row["name"]][:25]

    @app_commands.command(name="list", description="List conversion rules and their status in this channel")
    async def list_fixers(self, interaction: discord.Interaction):
        rows = await self.rules()
        enabled = await self.bot.sqlite.fetch(
            "SELECT name FROM embedfix_channels WHERE channel_id = ?",
            interaction.channel_id
        )
        names = {row["name"] for row in enabled}
        if not rows:
            await interaction.response.send_message(
                "No rules yet. Add one with `/embedfix add`.", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        for start in range(0, len(rows), 10):
            embed = discord.Embed(title="Embedfix", color=config.Color_Default)
            for row in rows[start:start + 10]:
                status = "ON" if row["name"] in names else "OFF"
                embed.add_field(
                    name=f"{row['name']} - {status}",
                    value=f"`{row['source']}` -> `{row['target']}`", inline=False
                )
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def save_rule(self, interaction, name, source, target, edit=False):
        if not re.fullmatch(r"[a-z0-9_-]{1,32}", name):
            await interaction.response.send_message("Use a short name like instagram or twitter.", ephemeral=True)
            return
        try:
            source = parse_domain(source)
            target = parse_domain(target)
            if source == target:
                raise ValueError("Source and target must be different.")
            if edit:
                await self.bot.sqlite.execute(
                    "UPDATE embedfix_rules SET source = ?, target = ? WHERE name = ?",
                    source, target, name
                )
            else:
                await self.bot.sqlite.execute(
                    "INSERT INTO embedfix_rules (name, source, target) VALUES (?, ?, ?)",
                    name, source, target
                )
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return
        except sqlite3.IntegrityError:
            await interaction.response.send_message("That name or source domain is already used.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"Saved **{name}**: `{source}` -> `{target}`. Use `/embedfix toggle` to enable it here.",
            ephemeral=True
        )

    @app_commands.command(name="add", description="Add a conversion rule")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def add(self, interaction: discord.Interaction, name: str, source: str, target: str):
        name = name.strip().lower()
        rule = await self.bot.sqlite.fetchrow("SELECT name FROM embedfix_rules WHERE name = ?", name)
        if rule:
            await interaction.response.send_message("That name already exists. Use `/embedfix edit`.", ephemeral=True)
            return
        await self.save_rule(interaction, name, source, target)

    @app_commands.command(name="edit", description="Change the detected or replacement domain")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.autocomplete(name=fixer_autocomplete)
    async def edit(self, interaction: discord.Interaction, name: str, source: str, target: str):
        name = name.strip().lower()
        rule = await self.bot.sqlite.fetchrow("SELECT name FROM embedfix_rules WHERE name = ?", name)
        if not rule:
            await interaction.response.send_message("That rule doesn't exist.", ephemeral=True)
            return
        await self.save_rule(interaction, name, source, target, edit=True)

    @app_commands.command(name="remove", description="Remove a rule and all its channel toggles")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.autocomplete(name=fixer_autocomplete)
    async def remove(self, interaction: discord.Interaction, name: str):
        changed = await self.bot.sqlite.execute(
            "DELETE FROM embedfix_rules WHERE name = ?",
            name.strip().lower()
        )
        await interaction.response.send_message(
            "Rule removed." if changed else "That rule doesn't exist.", ephemeral=True
        )

    @app_commands.command(name="toggle", description="Enable or disable a rule in this channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.autocomplete(name=fixer_autocomplete)
    async def toggle(self, interaction: discord.Interaction, name: str):
        name = name.strip().lower()
        rule = await self.bot.sqlite.fetchrow(
            "SELECT name FROM embedfix_rules WHERE name = ?",
            name
        )
        if not rule:
            await interaction.response.send_message("That rule doesn't exist.", ephemeral=True)
            return
        changed = await self.bot.sqlite.execute(
            "DELETE FROM embedfix_channels WHERE channel_id = ? AND name = ?",
            interaction.channel_id, name
        )
        if not changed:
            await self.bot.sqlite.execute(
                "INSERT OR IGNORE INTO embedfix_channels (channel_id, name) VALUES (?, ?)",
                interaction.channel_id, name
            )
        await interaction.response.send_message(
            f"**{name}** {'disabled' if changed else 'enabled'} in this channel.", ephemeral=True
        )

    @app_commands.command(name="all", description="Enable or disable all current rules in this channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_all(self, interaction: discord.Interaction):
        changed = await self.bot.sqlite.execute(
            "DELETE FROM embedfix_channels WHERE channel_id = ?",
            interaction.channel_id
        )
        if not changed:
            await self.bot.sqlite.execute(
                "INSERT OR IGNORE INTO embedfix_channels (channel_id, name) "
                "SELECT ?, name FROM embedfix_rules",
                interaction.channel_id
            )
        await interaction.response.send_message(
            f"All current rules {'disabled' if changed else 'enabled'} in this channel.", ephemeral=True
        )

    async def cog_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You need Manage Server to change embedfix.", ephemeral=True)
        else:
            raise error

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild or not URL_PATTERN.search(message.content):
            return
        # Reposting only text would discard attachments and stickers.
        if message.attachments or message.stickers:
            return
        rules = await self.bot.sqlite.fetch(
            "SELECT r.source, r.target FROM embedfix_rules r JOIN embedfix_channels c "
            "ON r.name = c.name WHERE c.channel_id = ?",
            message.channel.id
        )
        content = convert_links(message.content, rules)
        if content == message.content:
            return
        content = f"{message.author.mention} reposted:\n{content}"
        if len(content) > 2000:
            return
        permissions = message.channel.permissions_for(message.guild.me)
        if not permissions.manage_messages or not permissions.send_messages:
            return
        try:
            await message.channel.send(content, allowed_mentions=discord.AllowedMentions.none())
            await message.delete()
        except discord.HTTPException as exc:
            print(f"Failed to repost embedfix message: {exc}")


async def setup(bot):
    await bot.add_cog(Embedfix(bot))
