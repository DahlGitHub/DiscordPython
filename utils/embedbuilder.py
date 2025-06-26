import discord
from datetime import datetime
import config  # assumes your color & emoji constants are here

# Theme color mapping
THEME_COLORS = {
    "success": config.Color_Info,          # you can replace with a green tone
    "info": config.Color_Info,
    "warning": config.Color_Warning,
    "error": config.Color_Error,
    "default": config.Color_Default,
    "bot": config.Color_Bot,
    "reddit": config.Color_Module_Reddit,
    "timeedit": config.Color_Module_TimeEdit
}

class EmbedBuilder:
    def __init__(self, description=None, color=None, ctx=None):
        self.ctx = ctx  # Optional context for icon shortcuts
        resolved_color = self._resolve_color(color)
        self.embed = discord.Embed(
            description=description or "",
            color=discord.Color(resolved_color)
        )

    def _resolve_color(self, value):
        if isinstance(value, int):
            return value
        elif isinstance(value, str):
            return THEME_COLORS.get(value.lower(), config.Color_Default)
        return config.Color_Default

    def _resolve_icon(self, value):
        if not value:
            return None
        if isinstance(value, str):
            if not self.ctx:
                return value
            v = value.lower()
            if v == "server":
                return self.ctx.guild.icon.url if self.ctx.guild and self.ctx.guild.icon else None
            if v == "user":
                return self.ctx.author.display_avatar.url
            if v == "bot":
                return self.ctx.me.display_avatar.url
        return value  # direct URL or object with .url

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
        self.embed.timestamp = time or datetime.utcnow()
        return self

    def field(self, name=None, value=None, inline=False):
        if name and value:
            self.embed.add_field(name=name, value=value, inline=inline)
        return self

    def set_description(self, text=None):
        if text:
            self.embed.description = text
        return self

    def set_color(self, color=None):
        if color:
            self.embed.color = discord.Color(self._resolve_color(color))
        return self

    def theme(self, name):
        return self.set_color(name)

    def build(self):
        return self.embed
