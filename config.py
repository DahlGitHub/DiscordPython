import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_TOKEN = os.getenv('discord_token')
PREFIX = '.'

# Database
DATABASE_URL = os.getenv('database_url')

# Slash Commands Guilds
GUILDS = [596027534756544514]

# Color Variables
Color_Fatal = 0xB00020
Color_Error = 0xF8C300
Color_Warning = 0x686868
Color_Info = 0x007FFF
Color_Default = 0x7289DA

# Module Colors
Color_Bot = 0x7289DA
Color_Module_Reddit = 0xFF5700
Color_Module_TimeEdit = 0x138D75

# Error Log Channel ID
Error_Log_Channel_ID = 1388313577257042153  # Replace with your dev/log channel's ID
