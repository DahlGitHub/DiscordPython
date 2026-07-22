import os
from dotenv import load_dotenv
import random
import json

load_dotenv()

# Discord
DISCORD_TOKEN = os.getenv('discord_token')
PREFIX = os.getenv('discord_prefix')

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
RIOT_API_SERVER_EUW = os.getenv('riot_api_server_euwx')

SETUP_CATEGORIES = [
    "cogs.admin",
    "cogs.core",
    "cogs.utils",
]

GSPREAD_TEST = "https://docs.google.com/spreadsheets/d/1xBp5lE0r9Rf96qcbyaFcxixF2Wytclc8TtnIRFS1acg/edit?gid=0#gid=0" # Testing Sheet
GSPREAD_COBBLEMON = "https://docs.google.com/spreadsheets/d/1HRkD12dMLytrjx0mMWIPtu3lzY5j0Mi1_1SgRHW9zDM/edit?gid=369534627#gid=369534627"