"""Discord presentation for Steam wishlist pages and alerts."""

import asyncio
from urllib.parse import urljoin
import aiohttp
import discord
import config
from utils.paginator import ButtonPaginator
from utils.steam import SteamError, price_label


def promotion_card(item, end, free_to_keep, country):
    """One Steam offer per embed, with two-column metadata and header artwork."""
    kind = 'Free Game' if free_to_keep else 'Free Weekend'
    app_id = item['appid']
    embed = discord.Embed(
        title=f"{kind}: {item['name']}"[:256],
        url=f'https://store.steampowered.com/app/{app_id}/',
        color=0x1B92B5,
    )
    # Use a raster Steam logo so Discord can render the thumbnail.
    embed.set_thumbnail(url='https://store.cloudflare.steamstatic.com/public/shared/images/responsive/steam_share_image.jpg')
    options = list(item.get('purchase_options', []))
    options += [item.get('best_purchase_option') or {}, item.get('self_purchase_option') or {}]
    option = next((o for o in options if o.get('is_free_to_keep') and
                   o.get('free_to_keep_ends') == end), {}) if free_to_keep else (
                       item.get('best_purchase_option') or item.get('self_purchase_option') or {})
    original = option.get('formatted_original_price')
    price = (f'~~{original}~~ FREE' if original else 'FREE') if free_to_keep else (
        option.get('formatted_final_price') or 'Price unavailable')
    release = item.get('release') or {}
    released = release.get('steam_release_date') or release.get('original_steam_release_date')
    if free_to_keep:
        embed.add_field(name='Price', value=price)
        embed.add_field(name='Release Date', value=f'<t:{released}:D>' if released else 'Not announced')
    else:
        embed.add_field(name='Free until', value=f'<t:{end}:F>')
        embed.add_field(name='Price', value=price)
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    reviews = (item.get('reviews') or {}).get('summary_unfiltered') or {}
    count = reviews.get('review_count')
    percent = reviews.get('percent_positive')
    review_text = reviews.get('review_score_label') or 'Reviews unavailable'
    if count is not None and percent is not None:
        review_text += f' ({percent}% of {count:,} are positive)'
    platforms = item.get('platforms') or {}
    supported = [label for key, label in (('windows', 'Windows'), ('mac', 'Mac'),
                                         ('steamos_linux', 'Linux')) if platforms.get(key)]
    embed.add_field(name='All Reviews', value=review_text[:1024])
    embed.add_field(name='Supported Platforms', value=', '.join(supported) or 'Not specified')
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    if free_to_keep:
        embed.add_field(name='Claim before', value=f'<t:{end}:F>', inline=False)
    assets = item.get('assets') or {}
    filename = assets.get('header')
    template = assets.get('asset_url_format', '')
    artwork = template.replace('${FILENAME}', filename).replace('${APPID}', str(app_id)) if filename and template else (
        f'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{app_id}/header.jpg')
    # StoreBrowse returns paths such as steam/apps/570/header.jpg, not full URLs.
    artwork = urljoin('https://shared.fastly.steamstatic.com/store_item_assets/', artwork)
    embed.set_image(url=artwork)
    embed.set_footer(text=f'Steam | {country} | ' + ('Free to keep' if free_to_keep else 'Temporary free access'))
    return embed


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
