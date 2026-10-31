<p>
  <a href="https://pypi.python.org/pypi/discord.py"><img src="https://img.shields.io/pypi/v/discord.py.svg"></a>
  <a href="https://pypi.python.org/pypi/discord.py"><img src="https://img.shields.io/pypi/pyversions/discord.py.svg"></a>
  <a href="https://github.com/DahlGitHub/PythonProject/commits/main"></a><img src="https://img.shields.io/github/last-commit/DahlGitHub/PythonProject?color=blue"></a>
</p>

# ProjectPython
Discord bot with multiple functions, currently a small project with Olav.


Description
----

This is a hobby project program for a Discord bot made by using an API wrapper for Discord written in Python.
Discord.py - https://github.com/Rapptz/discord.py

## Local setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Use `.venv\Scripts\python.exe` as the Python interpreter in your IDE.
This keeps the bot's dependencies separate from your other Python projects.

Slash commands sync automatically for each server on startup, when joining a server,
and after owner cog load, reload, or unload commands. The admin `sync` command is still available.


Functionality
----

- **Steam:** Wishlist browsing, sale/release alerts, free-to-keep offers, and free weekends.
- **Riot / League of Legends:** Saved accounts, ranked stats, and patch notifications.
- **Ninja Kiwi / BTD6:** Player stats, recommended crosspaths, tier lists, and tower/hero references.
- **Canvas:** Courses, assignments, course subscriptions, and deadline reminders.
- **Cobblemon:** Pokédex lookups, types, moves, and spawn locations.
- **Minecraft:** CurseForge mod information.
- **Utilities:** Personal to-do lists, temporary reminders, and configurable link embed fixes.
- **Administration:** Server/user info, bot controls, and cog loading remembered in SQLite.
