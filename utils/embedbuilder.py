import discord
from datetime import datetime
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
    def __init__(self, title = None, url = None, description: str = None, type='rich', color: int = config.Color_Default):
        self.embed = discord.Embed(
            title=title,
            description=description,
            url=url,
            type=type,
            color=discord.Color(color))

    def __getattr__(self, attr):
        return getattr(self.embed, attr)
    
    def __repr__(self):
        return repr(self.embed)

    def _resolve_icon(self, icon_key):
        if isinstance(icon_key, str):
            if icon_key.startswith("http"):
                return icon_key
            return ICONS.get(icon_key)
        return None

    def author(self, name=None, icon=None):
        if name:
            self.embed.set_author(name=name, icon_url=self._resolve_icon(icon))
        return self

    def footer(self, text=None, icon=None):
        if text:
            self.embed.set_footer(text=text, icon_url=self._resolve_icon(icon))
        return self

    def image(self, url=None):
        if url:
            self.embed.set_image(url=url)
        return self

    def thumbnail(self, url=None):
        if url:
            self.embed.set_thumbnail(url=url)
        return self

    def timestamp(self, time=None):
        self.embed.timestamp = time or datetime.datetime.now()
        return self

    def field(self, name=None, value=None, inline=False):
        if name and value:
            self.embed.add_field(name=name, value=value, inline=inline)
        return self
