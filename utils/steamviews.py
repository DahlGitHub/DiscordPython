"""Discord presentation for Steam wishlist pages and alerts."""

import asyncio
import aiohttp
import discord
import config
from utils.paginator import ButtonPaginator
from utils.steam import SteamError, price_label


class WishlistPaginator(ButtonPaginator):
    def __init__(self, app_ids, member, steam_id, client):
        super().__init__([app_ids[i : i + 10] for i in range(0, len(app_ids), 10)])
        self.member = member
        self.steam_id = steam_id
        self.client = client
        self.total = len(app_ids)

    async def format_page(self, page):
        lines = []
        for app_id in page:
            try:
                game = await self.client.details(app_id)
                name = discord.utils.escape_markdown(game["name"])[:100]
                release = (game.get("release_date") or {}).get("date") or "Release TBA"
                extra = f" — {price_label(game)} • {release}"
            except (SteamError, aiohttp.ClientError, asyncio.TimeoutError):
                name, extra = f"App {app_id}", " — Details unavailable"
            lines.append(f"[{name}](https://store.steampowered.com/app/{app_id}/){extra}")
        embed = discord.Embed(
            title=f"{self.member.display_name} — Wishlist"[:256],
            description="\n".join(lines),
            color=config.Color_Default,
            url=f"https://store.steampowered.com/wishlist/profiles/{self.steam_id}/",
        )
        embed.set_footer(
            text=f"{self.total} games • Page {self.current_page + 1}/{self.max_pages} • {config.STEAM_COUNTRY}"
        )
        return embed

    async def update_page(self, interaction):
        # Steam lookups can exceed Discord's initial interaction deadline.
        await interaction.response.defer()
        self.update_buttons()
        kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
        kwargs.pop("files", None)
        await interaction.edit_original_response(**kwargs)


def notification(game, events, user_ids):
    app_id = game["steam_appid"]
    embed = discord.Embed(
        title=game["name"][:256],
        url=f"https://store.steampowered.com/app/{app_id}/",
        description=" • ".join(events),
        color=config.Color_Default,
    )
    embed.add_field(name="Price", value=price_label(game))
    release = game.get("release_date") or {}
    embed.add_field(name="Release", value=release.get("date") or "Not announced")
    # Discord descriptions support more text than fields; split large subscriber lists.
    mentions = [f"<@{user_id}>" for user_id in sorted(user_ids)]
    text = ", ".join(mentions)
    chunks = []
    while len(text) > 1024:
        split = text.rfind(", ", 0, 1024)
        chunks.append(text[:split])
        text = text[split + 2 :]
    chunks.append(text)
    for chunk in chunks[:20]:
        embed.add_field(name="Wishlisted by", value=chunk, inline=False)
    if len(chunks) > 20 or sum(len(f.value) for f in embed.fields) > 5000:
        embed.clear_fields()
        embed.add_field(name="Price", value=price_label(game))
        embed.add_field(name="Wishlisted by", value=f"{len(user_ids)} members — see attached list.")
    if game.get("header_image"):
        embed.set_image(url=game["header_image"])
    embed.set_footer(text=f"Steam • Prices for {config.STEAM_COUNTRY}")
    return embed
