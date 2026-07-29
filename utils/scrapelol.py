from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


PATCH_NOTES_URL = (
    "https://www.leagueoflegends.com/en-us/news/tags/patch-notes/"
)

BASE_URL = "https://www.leagueoflegends.com"

PATCH_URL_RE = re.compile(
    r"^/en-us/news/game-updates/"
    r"(?:league-of-legends-)?patch-[^/]+-notes/?$",
    re.IGNORECASE,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; DiscordPatchBot/1.0)"
    )
}


@dataclass(slots=True)
class LeaguePatch:
    title: str
    description: str
    url: str
    image_url: str | None


class PatchFetchError(RuntimeError):
    """Raised when Riot patch-note data cannot be fetched."""


def _get_soup(url: str) -> BeautifulSoup:
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        raise PatchFetchError(
            f"Failed to request Riot: {exc}"
        ) from exc

    return BeautifulSoup(
        response.text,
        "html.parser",
    )


def get_latest_patch_url() -> str:
    """
    Get the newest patch-note article URL from Riot's patch listing.
    """
    soup = _get_soup(PATCH_NOTES_URL)

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]

        # Remove query parameters if Riot adds tracking.
        clean_href = href.split("?", 1)[0]

        if PATCH_URL_RE.match(clean_href):
            return urljoin(
                BASE_URL,
                clean_href,
            )

    raise PatchFetchError(
        "Could not find the newest patch-note article."
    )


def _get_title(soup: BeautifulSoup) -> str:
    title_tag = soup.find("h1")

    if title_tag is None:
        raise PatchFetchError(
            "Could not find patch title."
        )

    return title_tag.get_text(
        " ",
        strip=True,
    )


def _get_description(
    soup: BeautifulSoup,
) -> str:
    """
    Riot puts the introductory patch summary in blockquote.context.
    """
    blockquote = soup.select_one(
        "blockquote.context"
    )

    if blockquote is None:
        return ""

    parts = [
        value.strip()
        for value in blockquote.stripped_strings
        if value.strip()
    ]

    return " ".join(parts)


def _get_patch_image(
    soup: BeautifulSoup,
) -> str | None:
    """
    Get the Patch Highlights image.

    Prefer an image in the Patch Highlights section,
    then fall back to Riot's content-border structure.
    """

    patch_heading = None

    for heading in soup.find_all(
        ["h2", "h3"]
    ):
        heading_text = heading.get_text(
            " ",
            strip=True,
        ).lower()

        if heading_text == "patch highlights":
            patch_heading = heading
            break

    if patch_heading is not None:
        for element in patch_heading.find_all_next():

            # Do not accidentally grab images from later sections.
            if (
                element.name == "h2"
                and element is not patch_heading
            ):
                break

            if element.name != "img":
                continue

            src = element.get("src")

            if src:
                return urljoin(
                    BASE_URL,
                    src,
                )

    # Fallback to the structure you found manually.
    image = soup.select_one(
        ".content-border "
        "img[src*='cmsassets.rgpub.io']"
    )

    if image:
        return image.get("src")

    return None


def get_latest_patch() -> LeaguePatch:
    """
    Fetch the newest League patch-note article and normalize
    the useful Discord information.
    """

    url = get_latest_patch_url()
    soup = _get_soup(url)

    return LeaguePatch(
        title=_get_title(soup),
        description=_get_description(soup),
        url=url,
        image_url=_get_patch_image(soup),
    )


if __name__ == "__main__":
    # Manual test:
    #
    # python -m utils.scrapelol

    patch = get_latest_patch()

    print(f"Title: {patch.title}")
    print(f"URL: {patch.url}")
    print(f"Image: {patch.image_url}")
    print()
    print(patch.description)