import os
from dotenv import load_dotenv

load_dotenv()

"""
CONFIGURATION FILE

"""

"""
Tokens, passwords etc.
"""
# Discord
DISCORD_TOKEN = os.getenv('discord_token')
# PREFIX = '.'
PREFIX = '~'

# Reddit
CLIENT_ID = os.getenv('reddit_id')
CLIENT_SECRET = os.getenv('reddit_secret')
USERNAME = os.getenv('reddit_username')
PASSWORD = os.getenv('reddit_password')
USER_AGENT = 'Python'

# ChatBot
CHAT_ID = os.getenv('chat_id')
CHAT_KEY = os.getenv('chat_key')
CHAT_URL = os.getenv('chat_url')

# API
SCRAPFLY_KEY = os.getenv('scrapfly_key')
RANDOMSTUFF_KEY = os.getenv('randomstuff_key')

GUILDS = [596027534756544514]

"""
Level System
"""
Random_Min_Xp = "30"
Random_Max_Xp = "45"
Level_Increment = "75" # Current Level * Increment + Previous Xp Level

"""
Color Variables, seperated by Type and Module
"""
# Type
Color_Error = 0xB00020
Color_Warning = 0xF8C300
Color_Info = 0x007FFF
Color_Default = 0xFFFFFF

# Module
Color_Bot = 0x7289DA
Color_Module_Reddit = 0xFF5700
Color_Module_TimeEdit = 0x138D75


Error_Log_Channel_ID = 1386844530262671471  # Replace with your dev/log channel's ID

"""
Emojis
"""
# Channels
Channel_News = "<:announcement:1048851567308197890>"
Channel_Nsfw = "<:textnsfw:737799550382637056>"
Channel_Lock = "<:textlock:737799550470717561>"
Channel_Text = "<:text:737752247240491122>"
Channel_Voice = "<:voice:737752247231840266>"
Channel_Voice_Lock = "<:voicelock:737799550084972665>"

# Type
Server_Emoji = "<:emotes:737760307489013801>"
Server_Roles = "<:roles:737758122529259650>"
Server_Category = "<:category:737752247873568798>"
Server_Member = "<:members:737752247525441891>"
Server_Bot = "<:bot:737752247483629628>"

# Status
Server_Owner = "<:owner:737752247403806782>"
Server_Mod = "<:ban:738117368420761711>"
Server_Boost = "<:booster:738117368907169873>"

Status_Online = "<:online:737752247127244902>"
Status_Offline = "<:offline:737752247357931572>"
Status_Idle = "<:idle:737752265837772842>"
Status_Dnd = "<:dnd:737752246804021340>"