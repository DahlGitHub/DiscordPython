import discord
from discord.ext import commands
import aiohttp
from utils.constraints import TIERLIST
from utils.embedbuilder import EmbedBuilder
from utils.types import EmbedResult
from datetime import datetime, timezone

class PublishCanvas(commands.Cog):

    @staticmethod
    async def fetch_announcements(key: str, course_id: int, since: datetime):
        url = "https://uia.instructure.com/api/v1/announcements"
        params = {
            "context_codes[]": f"course_{course_id}",
            "start_date": since.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        headers = {"Authorization": f"Bearer {key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    return []
                return await response.json()

    @staticmethod
    async def fetch_modules(key: str, course_id: int):
        base_url = f"https://uia.instructure.com/api/v1/courses/{course_id}/modules"
        headers = {"Authorization": f"Bearer {key}"}

        results = []
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, headers=headers) as resp:
                if resp.status != 200:
                    return []
                modules = await resp.json()

            for module in modules:
                if not module.get("published"):
                    continue
                async with session.get(module["items_url"], headers=headers) as resp_items:
                    if resp_items.status != 200:
                        continue
                    items = await resp_items.json()
                    for item in items:
                        if item.get("published", False):
                            results.append({"module": module, "item": item})
        return results

    @staticmethod
    async def fetch_assignments(key: str, course_id: int, since: datetime):
        url = f"https://uia.instructure.com/api/v1/courses/{course_id}/assignments"
        headers = {"Authorization": f"Bearer {key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return []
                return await response.json()

    @staticmethod
    async def build_embed(data, course_name: str, content_type: str, update_type: str = "new", module: dict = None) -> EmbedBuilder:
        if content_type == "announcement":
            return await PublishCanvas.build_announcement_embed(data, course_name, update_type)
        elif content_type == "module":
            return await PublishCanvas.build_module_embed(data, course_name, update_type, module)
        elif content_type == "assignment":
            return await PublishCanvas.build_assignment_embed(data, course_name, update_type)
        else:
            raise ValueError(f"Unknown content_type: {content_type}")

    @staticmethod
    async def build_announcement_embed(item, course_name, update_type):
        prefix_map = {
            "new": ("<:new:1399742653427613786>", "New"),
            "updated": ("<:updated:1399742637170360411>", "Updated"),
        }
        prefix_icon, prefix_text = prefix_map.get(update_type, (":pushpin:", "Notice"))

        posted_at_str = item.get("posted_at") or item.get("created_at")
        posted_at = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00")) if posted_at_str else datetime.now(timezone.utc)

        description = f"{prefix_icon} {prefix_text} Announcement:\n[{item.get('title', 'No Title')}]({item.get('html_url', '#')})"

        return (
            EmbedBuilder(description=description)
            .author(name=course_name, icon="https://cdn.discordapp.com/attachments/1386484077577900072/1399896085664895036/megaphone2.png")
            .footer(
                text=item.get("author", {}).get("display_name", "Unknown Author"),
                icon=item.get("author", {}).get("avatar_image_url"),
            )
            .timestamp(posted_at)
        )

    @staticmethod
    async def build_module_embed(items, course_name, update_type, module):
        prefix_icon, prefix_text = ("<:new:1399742653427613786>", "New Content in Module")

        if not isinstance(items, list):
            items = [items]

        description = f"{prefix_icon} {prefix_text} **{module['name']}**:\n"
        for item in items:
            description += f"- [{item.get('title', 'Untitled')}]({item.get('html_url', '#')})\n"

        posted_at = datetime.now(timezone.utc)

        return (
            EmbedBuilder(description=description)
            .author(name=course_name, icon="https://cdn.discordapp.com/attachments/1386484077577900072/1399897287160762439/clipboard-list5.png")
            .footer(text="Canvas Module Update")
            .timestamp(posted_at)
        )

    @staticmethod
    async def build_assignment_embed(item, course_name, update_type):
        prefix_map = {
            "new": ("<:new:1399742653427613786>", "New Assignment"),
            "updated": ("<:updated:1399742637170360411>", "Updated Assignment"),
        }
        prefix_icon, prefix_text = prefix_map.get(update_type, (":pushpin:", "Assignment"))

        description = f"{prefix_icon} {prefix_text}:\n- [{item.get('name', 'No Title')}]({item.get('html_url', '#')})"

        posted_at_str = item.get("updated_at") or item.get("created_at")
        posted_at = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00")) if posted_at_str else datetime.now(timezone.utc)

        embed = (
            EmbedBuilder(description=description)
            .author(name=course_name, icon="https://cdn.discordapp.com/attachments/1386484077577900072/1399896416377372875/square-pen2.png")
            .footer(text="Canvas Assignment")
            .timestamp(posted_at)
        )

        due_at = item.get("due_at")
        if due_at:
            due_dt = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
            due_unix = int(due_dt.timestamp())
            embed.field(
                name="Task Due",
                value=f"<t:{due_unix}:F>\n(<t:{due_unix}:R>)",
                inline=False,
            )

        return embed
    
async def setup(bot):
    await bot.add_cog(PublishCanvas(bot))