
from typing import Tuple, Union
import discord

"""
Shared type aliases used across bloons bot modules.
"""

UserDataResult = Tuple[discord.User | None, Union[dict, str]]

EmbedResult = Tuple[discord.Embed, bool]