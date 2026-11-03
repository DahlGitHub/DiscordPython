"""Persist manually selected bot presence."""

import discord

ACTIVITIES = {
    'playing': discord.ActivityType.playing,
    'watching': discord.ActivityType.watching,
    'listening': discord.ActivityType.listening,
    'competing': discord.ActivityType.competing,
    'streaming': discord.ActivityType.streaming,
}
STATUSES = {'online', 'idle', 'dnd', 'invisible'}


async def restore_presence(bot):
    row = await bot.sqlite.fetchrow('SELECT status, activity_type, message, url FROM bot_presence WHERE id = 1')
    if row is None:
        return
    activity = None
    if row['activity_type']:
        activity = discord.Activity(type=ACTIVITIES[row['activity_type']], name=row['message'], url=row['url'])
    await bot.change_presence(status=discord.Status(row['status']), activity=activity)


async def save_presence(bot, kind, message):
    kind = kind.lower()
    message = message.strip()
    row = await bot.sqlite.fetchrow('SELECT status, activity_type, message, url FROM bot_presence WHERE id = 1')
    status, activity_type, text, url = tuple(row) if row else ('online', None, '', None)
    if kind in STATUSES:
        if message:
            raise ValueError('Use online, idle, dnd, or invisible without a message.')
        status = kind
    elif kind == 'clear':
        if message:
            raise ValueError('Use clear without a message.')
        activity_type, text, url = None, '', None
    elif kind in ACTIVITIES:
        if not message or len(message) > 128:
            raise ValueError('Provide an activity message of 1–128 characters.')
        activity_type, text, url = kind, message, None
        if kind == 'streaming':
            url, _, text = message.partition(' ')
            if not text or not url.startswith(('https://www.twitch.tv/', 'https://twitch.tv/', 'https://www.youtube.com/', 'https://youtube.com/')):
                raise ValueError('Use streaming https://twitch.tv/channel Your stream title.')
    else:
        raise ValueError('Use playing, watching, listening, competing, streaming, online, idle, dnd, invisible, or clear.')
    await bot.sqlite.execute(
        'INSERT INTO bot_presence (id, status, activity_type, message, url) VALUES (1, ?, ?, ?, ?) '
        'ON CONFLICT(id) DO UPDATE SET status = excluded.status, activity_type = excluded.activity_type, '
        'message = excluded.message, url = excluded.url',
        status, activity_type, text, url,
    )
    await restore_presence(bot)
