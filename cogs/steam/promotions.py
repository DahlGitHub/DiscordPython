"""Scheduled Steam promotion posts, with persistent per-server deduplication."""

import asyncio
import datetime
import logging
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord.ext import commands, tasks

import config
from utils.steam import SteamClient
from utils.steampromos import promotion_items, free_games, free_weekend_games
from utils.steamviews import promotion_card

log = logging.getLogger(__name__)
OSLO = ZoneInfo('Europe/Oslo')


class SteamPromotions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()

    async def cog_load(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        self.free_checker.start()
        self.weekend_checker.start()

    async def cog_unload(self):
        self.free_checker.cancel()
        self.weekend_checker.cancel()
        await self.session.close()

    async def check(self, kind, guild_id=None):
        async with self.lock:
            rows = await self.bot.sqlite.fetch(
                'SELECT guild_id, channel_id FROM steam_promo_channels WHERE kind = ?', kind
            )
            rows = [row for row in rows if guild_id is None or row['guild_id'] == guild_id]
            if not rows:
                return 0, 0
            client = SteamClient(self.session, config.STEAM_API_KEY, config.STEAM_COUNTRY)
            items = await promotion_items(client)
            offers = (free_games if kind == 'freegames' else free_weekend_games)(items)
            posted = 0
            failed = 0
            for row in rows:
                try:
                    channel = self.bot.get_channel(row['channel_id'])
                    if channel is None:
                        channel = await self.bot.fetch_channel(row['channel_id'])
                    if not isinstance(channel, discord.TextChannel) or channel.guild.id != row['guild_id']:
                        failed += 1
                        continue
                    for item, end in offers:
                        key = (row['guild_id'], kind, item['appid'], end)
                        exists = await self.bot.sqlite.fetchrow(
                            'SELECT 1 FROM steam_promo_posts WHERE guild_id = ? AND kind = ? AND app_id = ? AND offer_end = ?', *key
                        )
                        if exists:
                            continue
                        await channel.send(
                            embed=promotion_card(item, end, kind == 'freegames', config.STEAM_COUNTRY),
                            allowed_mentions=discord.AllowedMentions.none(),
                        )
                        await self.bot.sqlite.execute(
                            'INSERT OR IGNORE INTO steam_promo_posts VALUES (?, ?, ?, ?)', *key
                        )
                        posted += 1
                except discord.HTTPException as exc:
                    failed += 1
                    log.warning('Steam promotions failed for guild %s (Discord code %s)', row['guild_id'], exc.code)
            return posted, failed

    async def scheduled_check(self, kind):
        try:
            await self.check(kind)
        except Exception as exc:
            log.error('Steam %s check failed (%s); retrying next scheduled check', kind, type(exc).__name__)

    @tasks.loop(hours=12)
    async def free_checker(self):
        await self.scheduled_check('freegames')

    @tasks.loop(time=datetime.time(hour=18, tzinfo=OSLO))
    async def weekend_checker(self):
        if datetime.datetime.now(OSLO).weekday() == 3:
            await self.scheduled_check('freeweekends')

    @free_checker.before_loop
    @weekend_checker.before_loop
    async def before_checks(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(SteamPromotions(bot))
