"""Steam-only HTTP client and wishlist notification rules."""

import asyncio
import re
from urllib.parse import urlparse


class SteamError(Exception):
    pass


def profile_identifier(value):
    value = value.strip()
    if value.isdigit() and len(value) == 17:
        return value, False
    if "://" in value or value.startswith("steamcommunity.com/"):
        parsed = urlparse(value if "://" in value else "https://" + value)
        parts = parsed.path.strip("/").split("/")
        if parsed.hostname != "steamcommunity.com" or len(parts) != 2:
            raise SteamError("Use a SteamID64 or a Steam community profile URL.")
        kind, value = parts
        if kind == "profiles" and value.isdigit() and len(value) == 17:
            return value, False
        if kind != "id":
            raise SteamError("Use a /profiles/ or /id/ Steam profile URL.")
    if not re.fullmatch(r"[A-Za-z0-9_-]{2,64}", value):
        raise SteamError("Invalid Steam profile name or SteamID64.")
    return value, True


class SteamClient:
    def __init__(self, session, key=None, country="NO"):
        self.session = session
        self.key = key
        self.country = country.lower()
        self.details_cache = {}
        self.wishlist_cache = {}

    async def request(self, url, **params):
        await asyncio.sleep(0.5)
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                # Do not expose request URLs, which may contain the API key.
                raise SteamError(f"Steam returned HTTP {response.status}. Try again later.")
            try:
                data = await response.json(content_type=None)
            except ValueError:
                raise SteamError("Steam returned an invalid response. Try again later.") from None
            if not isinstance(data, dict):
                raise SteamError("Steam returned an unexpected response.")
            return data

    async def resolve(self, profile):
        value, vanity = profile_identifier(profile)
        if not vanity:
            return value
        if not self.key:
            raise SteamError("Set steam_api_key in .env, or supply a numeric SteamID64.")
        data = await self.request(
            "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/",
            key=self.key,
            vanityurl=value,
        )
        result = data.get("response", {})
        if not isinstance(result, dict) or result.get("success") != 1 or not result.get("steamid"):
            raise SteamError("Steam profile not found.")
        return str(result["steamid"])

    async def wishlist(self, steam_id):
        if steam_id in self.wishlist_cache:
            return self.wishlist_cache[steam_id]
        data = await self.request(
            "https://api.steampowered.com/IWishlistService/GetWishlist/v1/",
            steamid=steam_id,
        )
        result = data.get("response")
        if not isinstance(result, dict) or not isinstance(result.get("items"), list):
            raise SteamError(
                "Wishlist unavailable. Make it public; Steam may also be temporarily unavailable."
            )
        try:
            app_ids = sorted({int(item["appid"]) for item in result["items"]})
        except (KeyError, TypeError, ValueError):
            raise SteamError("Steam returned an invalid wishlist.") from None
        self.wishlist_cache[steam_id] = app_ids
        return app_ids

    async def details(self, app_id):
        if app_id not in self.details_cache:
            data = await self.request(
                "https://store.steampowered.com/api/appdetails",
                appids=app_id,
                cc=self.country,
                l="english",
            )
            result = data.get(str(app_id), {})
            if (
                not isinstance(result, dict)
                or not result.get("success")
                or not isinstance(result.get("data"), dict)
            ):
                raise SteamError(f"Store details unavailable for app {app_id}.")
            self.details_cache[app_id] = result["data"]
        return self.details_cache[app_id]


def game_state(game, country):
    release = game.get("release_date") or {}
    price = game.get("price_overview") or {}
    return {
        "country": country.upper(),
        "currency": price.get("currency"),
        "price": price.get("final"),
        "discount": price.get("discount_percent", 0),
        "coming_soon": release.get("coming_soon"),
        "date": release.get("date", ""),
    }


def changes(previous, current):
    """First observations can announce sales, but never historical releases."""
    events = []
    same_market = False
    if previous:
        same_country = previous["country"] == current["country"]
        same_currency = previous["currency"] == current["currency"]
        same_market = same_country and same_currency

    if current["discount"] > 0 and current["price"] is not None:
        first_price = previous is None or (
            previous["country"] == current["country"] and previous["price"] is None
        )
        new_sale = previous and not previous["discount"]
        cheaper = (
            previous and previous["price"] is not None and current["price"] < previous["price"]
        )
        if first_price or (same_market and (new_sale or cheaper)):
            events.append("On sale")
    if previous:
        if previous["coming_soon"] is True and current["coming_soon"] is False:
            events.append("Now available")
        elif (
            current["coming_soon"] is True
            and current["date"]
            and previous["date"] != current["date"]
        ):
            events.append("Release date updated")
    return events


def price_label(game):
    price = game.get("price_overview") or {}
    label = price.get("final_formatted")
    if not label and price.get("final") is not None:
        label = f"{price['final'] / 100:.2f} {price.get('currency', '')}".strip()
    if label and price.get("discount_percent", 0):
        return f"{label} (-{price['discount_percent']}%)"
    return label or ("Free to play" if game.get("is_free") else "Price unavailable")
