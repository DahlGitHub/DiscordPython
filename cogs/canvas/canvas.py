import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta
from discord import app_commands
from collections import defaultdict

from utils.paginator import ButtonPaginator

from .subscribecanvas import SubscribeCanvas
from .publishcanvas import PublishCanvas


class Canvas(commands.GroupCog, name="canvas"):
    REMINDER_OFFSETS = [
        timedelta(days=3),  # replace with days=7 later
        timedelta(days=1),  # replace with days=3 later
        timedelta(hours=12),  # replace with hours=24 later
    ]

    def __init__(self, bot):
        self.bot = bot
        self.last_checked = datetime.now(timezone.utc)
        self.announcement_cache = {}
        self.module_cache = {}
        self.assignment_cache = {}
        self.reminder_cache = {} 
        self.warmed_up = False 
        self.check_updates.start()
        self.check_reminders.start()

    def cog_unload(self):
        self.check_updates.cancel()
        self.check_reminders.cancel()

    # === Commands ===
    @commands.is_owner()
    @commands.command(name="term")
    async def term(self, ctx, term_id: int):
        await self.bot.db.execute(
            """
            INSERT INTO canvas_term (id, term_id)
            VALUES (1, $1)
            ON CONFLICT (id) DO UPDATE
            SET term_id = EXCLUDED.term_id
            """,
            term_id,
        )
        await ctx.send(f"✅ Current Canvas term set to **{term_id}**")

    @app_commands.command(name="key", description="Set your Canvas API key")
    async def key(self, interaction: discord.Interaction, key: str):
        await self.bot.db.execute(
            """
            INSERT INTO canvas_key (user_id, key)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
            SET key = EXCLUDED.key
            """,
            interaction.user.id,
            key,
        )
        await interaction.response.send_message(f"✅ Your Canvas key has been set.", ephemeral=True)

    @app_commands.command(name="courses", description="See your Canvas courses")
    async def courses(self, interaction: discord.Interaction):
        embed, ephemeral = await SubscribeCanvas.get_courses(self.bot.db, interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @app_commands.command(name="assignments", description="Get an overview of your assignments for subscribed courses")
    async def assignments(self, interaction: discord.Interaction):
        pages, ephemeral = await SubscribeCanvas.get_assignments(self.bot.db, interaction.user)

        if not pages:
            return await interaction.response.send_message("No assignments found.", ephemeral=True)

        if len(pages) == 1:
            await interaction.response.send_message(embed=pages[0], ephemeral=ephemeral)
        else:
            paginator = ButtonPaginator(pages=pages, author_id=interaction.user.id)
            await paginator.start(interaction)

    @app_commands.command(name="subscribe", description="Subscribe to a Canvas course")
    @app_commands.describe(course_id="The ID of the course to subscribe to", channel="The channel to receive updates in")
    async def subscribe(self, interaction: discord.Interaction, course_id: str, channel: discord.TextChannel):
        embed, error = await SubscribeCanvas.subscribe_to_course(self.bot.db, interaction.user, course_id, channel)
        await interaction.response.send_message(embed=embed, ephemeral=(error is not None))

    @app_commands.command(name="unsubscribe", description="Unsubscribe from a Canvas course")
    @app_commands.describe(course_id="The ID of the course to unsubscribe from")
    async def unsubscribe(self, interaction: discord.Interaction, course_id: str):
        embed, error = await SubscribeCanvas.unsubscribe_from_course(self.bot.db, interaction.user, course_id)
        await interaction.response.send_message(embed=embed, ephemeral=(error is not None))

    async def course_autocomplete(self, interaction: discord.Interaction, current: str):
        courses = await SubscribeCanvas.fetch_raw_courses(self.bot.db, interaction.user)
        if not courses:
            return []
        return [
            app_commands.Choice(name=f"{c['name']} (#{c['id']})", value=str(c["id"]))
            for c in courses
            if current.lower() in c["name"].lower()
        ][:25]

    @subscribe.autocomplete("course_id")
    @unsubscribe.autocomplete("course_id")
    async def shared_autocomplete(self, interaction: discord.Interaction, current: str):
        return await self.course_autocomplete(interaction, current)

    # === Handlers ===
    async def handle_announcements(self, key, course_id, course_name, channel, since, new_last_checked):
        announcements = await PublishCanvas.fetch_announcements(key, course_id, since)

        if not self.warmed_up:
            for ann in announcements:
                self.announcement_cache[ann["id"]] = ann.get("message", "")
            return new_last_checked

        for ann in announcements:
            ann_id = ann["id"]
            message_body = ann.get("message", "")

            posted_at = datetime.fromisoformat(
                ann["posted_at"].replace("Z", "+00:00")
            ).astimezone(timezone.utc)

            last_reply_at = datetime.fromisoformat(
                ann["last_reply_at"].replace("Z", "+00:00")
            ).astimezone(timezone.utc) if ann.get("last_reply_at") else posted_at

            update_type = None
            if ann_id not in self.announcement_cache and posted_at > self.last_checked:
                update_type = "new"
            elif last_reply_at > self.last_checked and self.announcement_cache.get(ann_id) != message_body:
                update_type = "updated"

            if update_type:
                embed = await PublishCanvas.build_embed(ann, course_name, content_type="announcement", update_type=update_type)
                await channel.send(embed=embed)

            new_last_checked = max(new_last_checked, posted_at, last_reply_at)
            self.announcement_cache[ann_id] = message_body

        return new_last_checked

    async def handle_modules(self, key, course_id, course_name, channel):
        modules = await PublishCanvas.fetch_modules(key, course_id)

        if not self.warmed_up:
            if course_id not in self.module_cache:
                self.module_cache[course_id] = set()
            for entry in modules:
                self.module_cache[course_id].add(entry["item"]["id"])
            return

        new_items_by_module = defaultdict(list)
        for entry in modules:
            module, item = entry["module"], entry["item"]
            item_id = item["id"]

            if course_id not in self.module_cache:
                self.module_cache[course_id] = set()

            if item_id not in self.module_cache[course_id]:
                new_items_by_module[module["id"]].append((module, item))
                self.module_cache[course_id].add(item_id)

        for _, entries in new_items_by_module.items():
            module = entries[0][0]
            items = [e[1] for e in entries]

            embed = await PublishCanvas.build_embed(
                items, course_name, content_type="module", update_type="new_content", module=module
            )
            await channel.send(embed=embed)

    async def handle_assignments(self, key, course_id, course_name, channel, since, new_last_checked):
        assignments = await PublishCanvas.fetch_assignments(key, course_id, since)

        if not self.warmed_up:
            if course_id not in self.assignment_cache:
                self.assignment_cache[course_id] = {}
            for assn in assignments:
                if assn.get("published") and assn.get("workflow_state") == "published":
                    self.assignment_cache[course_id][assn["id"]] = {
                        "name": assn.get("name"),
                        "due_at": assn.get("due_at"),
                        "points_possible": assn.get("points_possible"),
                        "updated_at": assn.get("updated_at"),
                    }
            return new_last_checked

        if course_id not in self.assignment_cache:
            self.assignment_cache[course_id] = {}

        for assn in assignments:
            if not (assn.get("published") and assn.get("workflow_state") == "published"):
                continue

            assn_id = assn["id"]
            posted_at_str = assn.get("updated_at") or assn.get("created_at")
            posted_at = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00")) if posted_at_str else datetime.now(timezone.utc)

            cached = self.assignment_cache[course_id].get(assn_id)
            update_type = None

            if cached is None:
                update_type = "new"
            else:
                if (
                    cached.get("due_at") != assn.get("due_at")
                    or cached.get("points_possible") != assn.get("points_possible")
                    or cached.get("updated_at") != assn.get("updated_at")
                ):
                    update_type = "updated"

            if update_type:
                embed = await PublishCanvas.build_embed(assn, course_name, content_type="assignment", update_type=update_type)
                await channel.send(embed=embed)

            self.assignment_cache[course_id][assn_id] = {
                "name": assn.get("name"),
                "due_at": assn.get("due_at"),
                "points_possible": assn.get("points_possible"),
                "updated_at": assn.get("updated_at"),
            }

            new_last_checked = max(new_last_checked, posted_at)

        return new_last_checked

    # === Main update loop ===
    @tasks.loop(seconds=600)
    async def check_updates(self):
        try:
            print("🔄 check_updates tick")
            new_last_checked = self.last_checked

            rows = await self.bot.db.fetch("SELECT user_id, course_id, channel_id FROM canvas_subscriptions")
            for row in rows:
                user_id, course_id, channel_id = row["user_id"], row["course_id"], row["channel_id"]

                key = await self.bot.db.fetchval("SELECT key FROM canvas_key WHERE user_id = $1", user_id)
                if not key:
                    continue

                courses = await SubscribeCanvas.fetch_raw_courses(self.bot.db, discord.Object(user_id))
                course_lookup = {int(c["id"]): c.get("name", "Unknown Course") for c in (courses or [])}
                course_name = course_lookup.get(course_id, f"Course {course_id}")

                channel = self.bot.get_channel(channel_id)
                if not channel:
                    continue

                grace_period = timedelta(minutes=2)
                since = self.last_checked - grace_period

                new_last_checked = await self.handle_announcements(key, course_id, course_name, channel, since, new_last_checked)
                await self.handle_modules(key, course_id, course_name, channel)
                new_last_checked = await self.handle_assignments(key, course_id, course_name, channel, since, new_last_checked)

            self.last_checked = new_last_checked
            self.warmed_up = True

        except Exception as e:
            print(f"❌ Error in check_updates: {e}")

    # === Reminder loop ===
    @tasks.loop(seconds=30)
    async def check_reminders(self):
        try:
            now = datetime.now(timezone.utc)
            rows = await self.bot.db.fetch("SELECT course_id, channel_id FROM canvas_subscriptions")
            for row in rows:
                course_id, channel_id = row["course_id"], row["channel_id"]

                if course_id not in self.assignment_cache:
                    continue

                channel = self.bot.get_channel(channel_id)
                if not channel:
                    continue

                for assn_id, assn_data in self.assignment_cache[course_id].items():
                    due_at_str = assn_data.get("due_at")
                    if not due_at_str:
                        continue

                    due_at = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
                    if due_at < now:
                        continue  # already passed

                    for i, offset in enumerate(self.REMINDER_OFFSETS):
                        reminder_time = due_at - offset
                        if reminder_time <= now < reminder_time + timedelta(minutes=1):
                            reminded_stages = self.reminder_cache.setdefault(course_id, {}).setdefault(assn_id, {})
                            if reminded_stages.get(i):
                                continue

                            embed = discord.Embed(
                                title="⏰ Assignment Reminder",
                                description=f"**{assn_data.get('name', 'Unnamed Assignment')}** is due soon!",
                            )
                            embed.add_field(
                                name="Due",
                                value=f"<t:{int(due_at.timestamp())}:F> (<t:{int(due_at.timestamp())}:R>)",
                                inline=False
                            )
                            embed.set_footer(text=f"Reminder Stage {i+1}")

                            await channel.send(embed=embed)
                            reminded_stages[i] = True
                            print(f"✅ Sent stage {i+1} reminder for {assn_data.get('name')}")

        except Exception as e:
            print(f"❌ Error in check_reminders: {e}")


async def setup(bot):
    await bot.add_cog(Canvas(bot))
