import os
from dotenv import load_dotenv
import random

load_dotenv()

# Discord
DISCORD_TOKEN = os.getenv('discord_token')
# PREFIX = '.'
PREFIX = '~'

# Database
DATABASE_URL = os.getenv('database_url')

# Slash Commands Guilds
GUILDS = [596027534756544514]
DISCORD_APPLICATION_ID = os.getenv('discord_application_id')

# Color Variables
Color_Fatal = 0xB00020
Color_Error = 0xF8C300
Color_Warning = 0x686868

Color_Default = 0x7289DA
Color_Bloons = 0xFF0000
Color_Random = random.randint(0, 0xFFFFFF)

# Error Log Channel ID
Error_Log_Channel_ID = 1388313577257042153  # Replace with your dev/log channel's ID

#riotgames api
RIOT_API_KEY = os.getenv('riot_api_key')
RIOT_API_REGION = os.getenv('riot_api_region')
RIOT_API_SERVER_EUW = os.getenv('riot_api_server_euw')