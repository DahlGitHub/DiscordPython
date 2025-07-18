import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands
from utils.time import parse_time_and_message, human_timedelta
from utils.embedbuilder import EmbedBuilder


MAX_DELTA = timedelta(days=7)


class ReminderCog(commands.GroupCog, name="reminder", description="Temporary in-memory reminders"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminders: dict[int, list[tuple[datetime, str, asyncio.Task]]] = {}

    @app_commands.command(name="set", description="Set a reminder (max 7 days)")
    @app_commands.describe(when="When to be reminded of something.")
    async def set(self, interaction: discord.Interaction, *, when: str):
        when, message = parse_time_and_message(when)
        if when is None:
            embed = (
                EmbedBuilder(
                    description=(
                        "Examples:\n"
                        "• `in 2h drink water`\n"
                        "• `next tuesday at 9am meeting`"
                    )
                )
                .author(name="Couldn’t understand that time.")
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        now = datetime.now(timezone.utc)
        if not (now < when <= now + MAX_DELTA):
            return await interaction.response.send_message(
                "Reminders must be within **0 – 7 days** from now.", ephemeral=True
            )
        task = asyncio.create_task(
            self._deliver(interaction.channel, interaction.user, when, message)
        )

        self.reminders.setdefault(interaction.user.id, []).append((when, message, task))

        await interaction.response.send_message(
            f"Okay {interaction.user.mention}! I’ll remind you in {human_timedelta(when, now)}."
        )

    @app_commands.command(name="list", description="List your current reminders")
    async def list(self, interaction: discord.Interaction):
        user_rems = self.reminders.get(interaction.user.id, [])
        if not user_rems:
            return await interaction.response.send_message(
                "You have no active reminders.", ephemeral=True
            )

        user_rems.sort(key=lambda r: r[0])
        lines = [
            f"**{i+1}.** <t:{int(rem[0].timestamp())}:R> – {rem[1]}"
            for i, rem in enumerate(sorted(user_rems, key=lambda r: r[0]))
        ]
        embed = EmbedBuilder(description="\n".join(lines)).author(
            name=f"{interaction.user.display_name}'s Reminders",
            icon=interaction.user.display_avatar,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove", description="Remove a reminder by its list number")
    async def remove(self, interaction: discord.Interaction, id: int):
        user_rems = self.reminders.get(interaction.user.id, [])
        if id < 1 or id > len(user_rems):
            return await interaction.response.send_message("No such reminder.", ephemeral=True)

        when, msg, task = user_rems.pop(id - 1)
        task.cancel()

        await interaction.response.send_message(
            f"Removed reminder **#{id}** (<t:{int(when.timestamp())}:R> – {msg}).",
            ephemeral=True,
        )

    async def _deliver(
        self,
        channel: discord.TextChannel,
        user: discord.User | discord.Member,
        when: datetime,
        message: str,
    ):
        try:
            await discord.utils.sleep_until(when)
            await channel.send(f"{user.mention}, <t:{int(when.timestamp())}:R>: {message}")
        except asyncio.CancelledError:
            return
        finally:
            rems = self.reminders.get(user.id, [])
            self.reminders[user.id] = [r for r in rems if not (r[0] == when and r[1] == message)]
            if not self.reminders[user.id]: 
                del self.reminders[user.id]

    async def cog_unload(self):
        for rems in self.reminders.values():
            for _, _, task in rems: 
                task.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(ReminderCog(bot))
