import discord
from datetime import datetime, timezone
from typing_extensions import Self
import config  # assumes your color & emoji constants are here
from .icons import ICONS

class EmbedBuilder:
    """
    A custom class to build Discord embeds with a fluent interface.

    Usage:
    embed = EmbedBuilder(description="Your description here", color=config.Color_Default)
        .author(name="Author Name", icon="user")
        .footer(text="Footer text", icon="server")
        .image(url="https://example.com/image.png")
        .thumbnail(url="https://example.com/thumbnail.png")
        .timestamp()
        .field(name="Field Name", value="Field Value", inline=True)
        .set_description("Updated description")
        .set_color(config.Color_Info)
        .build()
    """
    def __init__(self, title = None, url = None, description: str = None, type='rich', color: int | discord.Color | None = config.Color_Default):
        self.embed = discord.Embed(
            title=title,
            description=description,
            url=url,
            type=type,
            color=color)

    def __getattr__(self, attr):
        return getattr(self.embed, attr)
    
    def __repr__(self):
        return repr(self.embed)

    @property
    def description(self):
        return self.embed.description

    @description.setter
    def description(self, value):
        self.embed.description = value

    @property
    def title(self):
        return self.embed.title

    @title.setter
    def title(self, value):
        self.embed.title = value

    @property
    def color(self):
        return self.embed.color

    @color.setter
    def color(self, value):
        self.embed.color = value

    def set_title(self, value: str | None) -> Self:
        self.title = value
        return self

    def set_description(self, value: str | None) -> Self:
        self.description = value
        return self

    def set_color(self, value: int | discord.Color | None) -> Self:
        self.color = value
        return self

    def build(self) -> discord.Embed:
        """Return the underlying embed, ready to send."""
        return self.embed

    def _resolve_icon(self, icon_key: str | discord.Asset | None) -> str | None:
        if isinstance(icon_key, discord.Asset):
            return str(icon_key)
        if isinstance(icon_key, str):
            if icon_key.lower().startswith(("http://", "https://")):
                return icon_key
            return ICONS.get(icon_key.lower())
        return None

    def author(self, name: str | None = None, icon: str | discord.Asset | None = None, *, url: str | None = None) -> Self:
        """Set an author with an icon key, URL, or Discord asset, and optional link."""
        if name:
            self.embed.set_author(name=name, icon_url=self._resolve_icon(icon), url=url)
        return self

    def footer(self, text: str | None = None, icon: str | discord.Asset | None = None) -> Self:
        if text:
            self.embed.set_footer(text=text, icon_url=self._resolve_icon(icon))
        return self

    def image(self, url: str | discord.Asset | None = None) -> Self:
        if url:
            self.embed.set_image(url=url)
        return self

    def thumbnail(self, url: str | discord.Asset | None = None) -> Self:
        if url:
            self.embed.set_thumbnail(url=url)
        return self

    def timestamp(self, time: datetime | None = None) -> Self:
        self.embed.timestamp = time or datetime.now(timezone.utc)
        return self

    def field(self, name=None, value=None, inline: bool = False) -> Self:
        if name and value is not None:
            self.embed.add_field(name=name, value=value, inline=inline)
        return self
