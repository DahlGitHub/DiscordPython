import discord
from discord.ext import commands
import aiohttp
from datetime import datetime, timezone, timedelta
from cogs.canvas.publishcanvas import PublishCanvas
from utils.embedbuilder import EmbedBuilder
from utils.types import EmbedResult, PaginationResult

class SubscribeCanvas(commands.Cog):

    course_cache = {}

    @staticmethod
    async def get_canvas_key(db, user: discord.User) -> EmbedResult:
        row = await db.fetchrow("SELECT key FROM canvas_key WHERE user_id = $1", user.id)
        if not row:
            return (
                EmbedBuilder(description=f"No Canvas key found for {user.mention}. Use `/canvas key` to set it."),
                True
            )
        return row["key"], False

    @staticmethod
    async def fetch_raw_courses(db, user: discord.User):
        now = datetime.utcnow()
        cached = SubscribeCanvas.course_cache.get(user.id)
        if cached and cached[1] > now:
            return cached[0]

        key, error = await SubscribeCanvas.get_canvas_key(db, user)
        if not key:
            return None

        url = "https://uia.instructure.com/api/v1/courses"
        headers = {"Authorization": f"Bearer {key}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return None
                courses = await resp.json()

        SubscribeCanvas.course_cache[user.id] = (courses, now + timedelta(minutes=60))
        return courses

    @staticmethod
    async def get_courses(db, user: discord.User) -> EmbedResult:
        courses = await SubscribeCanvas.fetch_raw_courses(db, user)
        if not courses:
            return (EmbedBuilder(description="Could not fetch courses from Canvas."), True)

        row = await db.fetchrow("SELECT term_id FROM canvas_term WHERE id = 1")
        if not row:
            return (EmbedBuilder(description="No active term set. Use `/term <id>` to set it."), True)
        current_term = row["term_id"]

        courses = [c for c in courses if c.get("enrollment_term_id") == current_term]

        rows = await db.fetch("SELECT course_id, channel_id FROM canvas_subscriptions WHERE user_id = $1", user.id)
        subs_lookup = {row["course_id"]: row["channel_id"] for row in rows}

        embed = EmbedBuilder().author(name=f"{user.name}'s Canvas Courses", icon="canvas")

        names_col = []
        channel_col = []

        for course in courses:
            cid = int(course["id"])
            names_col.append(f"[{course.get('course_code', 'Unknown')}](https://uia.instructure.com/courses/{course.get('id', '#')})")
            if cid in subs_lookup:
                channel_col.append(f"<#{subs_lookup[cid]}>")
            else:
                channel_col.append("-")

        if not names_col:
            embed.description = f"No courses found for term **{current_term}**."
            return embed, False

        embed.field(name="Course", value="\n".join(names_col), inline=True)
        embed.field(name="Channel", value="\n".join(channel_col), inline=True)
        return embed, False

    @staticmethod
    async def get_assignments(db, user: discord.User):
        from datetime import datetime

        row = await db.fetchrow("SELECT key FROM canvas_key WHERE user_id = $1", user.id)
        if not row:
            return ([EmbedBuilder(description=f"No Canvas key found for {user.mention}. Use `/canvas key` to set it.")], True)
        key = row["key"]

        subs = await db.fetch("SELECT course_id FROM canvas_subscriptions WHERE user_id = $1", user.id)
        if not subs:
            return ([EmbedBuilder(description="You’re not subscribed to any courses. Use `/canvas subscribe` first.")], True)

        row = await db.fetchrow("SELECT term_id FROM canvas_term WHERE id = 1")
        if not row:
            return ([EmbedBuilder(description="No active term set. Use `/term <id>` to set it.")], True)
        current_term = row["term_id"]


        courses = await SubscribeCanvas.fetch_raw_courses(db, user)
        course_lookup = {int(c["id"]): c for c in courses if c.get("enrollment_term_id") == current_term}

        pages = []
        for sub in subs:
            cid = sub["course_id"]

            course = course_lookup.get(cid)
            if not course:
                continue

            assignments = await PublishCanvas.fetch_assignments(key, cid, since=None)
            if not assignments:
                continue

            assignments = sorted(assignments, key=lambda a: a.get("due_at") or "9999-12-31T00:00:00Z")

            names_col = []
            due_col = []
            for a in assignments:
                names_col.append(f"[{a.get('name')}]({a.get('html_url', '#')})")
                due = a.get("due_at")
                if due:
                    try:
                        dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                        due_col.append(f"(<t:{int(dt.timestamp())}:R>)")
                    except Exception as e:
                        due_col.append("⚠️ parse error")
                else:
                    due_col.append("—")

            embed = EmbedBuilder().author(
                name=f"{user.name}'s Assignments",
                icon="canvas"
            )
            embed.title = course.get("course_code", "Unknown")
            embed.field("Assignment", "\n".join(names_col), inline=True)
            embed.field("Due", "\n".join(due_col), inline=True)
            embed.footer(text=f"{len(assignments)} assignments total")

            pages.append(embed)

        if not pages:
            return ([EmbedBuilder(description="No assignments found for your current subscriptions/term.")], True)

        return (pages, False)





    @staticmethod
    async def subscribe_to_course(db, user: discord.User, course_id: str, channel: discord.TextChannel):
        courses = await SubscribeCanvas.fetch_raw_courses(db, user)
        course = next((c for c in courses if str(c["id"]) == course_id), None)
        if not course:
            return EmbedBuilder(description="Invalid course ID. Use `/canvas courses` to view available ones."), True

        await db.execute(
            """
            INSERT INTO canvas_subscriptions (user_id, course_id, channel_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, course_id) DO UPDATE SET channel_id = $3
            """,
            user.id, int(course_id), channel.id
        )

        return EmbedBuilder(description=f"✅ Subscribed to **{course['name']}** (#{course_id}) in {channel.mention}."), False

    @staticmethod
    async def unsubscribe_from_course(db, user: discord.User, course_id: str):
        await db.execute(
            "DELETE FROM canvas_subscriptions WHERE user_id = $1 AND course_id = $2",
            user.id, int(course_id)
        )
        return EmbedBuilder(description=f"✅ Unsubscribed from course #{course_id}."), False


async def setup(bot: commands.Bot):
    await bot.add_cog(SubscribeCanvas(bot))