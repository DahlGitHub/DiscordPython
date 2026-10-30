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


Functionality
----
Description coming..

- Riot..
- Ninjakiwi..
- Canvas..
- More soon..
- Useful utility functions

## Steam wishlist alerts

Set `steam_api_key=YOUR_KEY` in `.env` to resolve custom Steam profile names.
Numeric SteamID64 registrations do not require a key. Set `steam_country=NO`
for Norwegian store prices (the default), or another two-letter store country.
Only Steam API endpoints are used; users must expose a public wishlist.

Steam uses slash commands (sync the command tree after loading the extension):

- `/steam add <SteamID64 or profile URL> [@member]`: register yourself or another member.
- `/steam remove [@member]`: remove a registration.
- `/steam users`: list registered members.
- `/steam wishlist [@member]`: browse a registered member's live wishlist with prices and release dates.
- `/steam setchannel #channel`: enable daily sale/release alerts for this server.
- `/steam check`: check immediately.
- `/steam disable`: stop alerts without deleting registrations.

Manage Server is required to manage another member or configure/run alerts.
Each game gets one post listing interested members, without pinging them.
The first check posts current sales and establishes a release baseline.
Later checks post new sales, further price drops, release-date changes, and
transitions from coming soon to available. State persists in SQLite across restarts.
No notifications are posted for historical releases on the first check.
Wishlist/store endpoints may change; unavailable data is retried rather than
treated as an empty wishlist. A confirmed empty `items` array is accepted.
