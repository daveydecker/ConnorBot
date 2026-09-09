# ConnorBot

A multi-purpose Discord bot built with `discord.py` that aggregates several external services behind a single command interface — live weather, game price tracking, Fortnite cosmetics lookup, and real-time smart-home sensor data pulled from a self-hosted Home Assistant instance.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2)

---

## Overview

ConnorBot started as a joke bot for a private server and grew into a working integration layer for five separate data sources. Each command is a self-contained handler that fetches from a remote API, normalizes an inconsistent response shape, and renders the result as a Discord embed or file attachment.

The parts worth reading:

- **Home Assistant integration** — queries live entity states from a self-hosted Home Assistant server over its REST API, exposing IoT sensor data (pet weight, litter box activity) as Discord commands. Timestamps are converted to Unix epoch and emitted as Discord's native relative-time markup so they stay accurate without polling.
- **Interactive reaction-driven selection** — the `!sale` command paginates ambiguous search results into a numbered embed, attaches reaction controls, and awaits user input asynchronously with `bot.wait_for` under a 30-second timeout, with an author-and-message-scoped predicate so one user's reaction can't hijack another's prompt.
- **Fuzzy matching** — Fortnite cosmetic lookups run through `difflib.get_close_matches` against a normalized name index, so partial or misspelled queries still resolve to the right skin.
- **Defensive response parsing** — external APIs return sparse and inconsistent records; the cosmetics filter chains existence checks across nested optional fields and falls back from `featured` to `icon` artwork rather than raising on a missing key.
- **Attachment ingestion pipeline** — an `on_message` listener watches a designated channel, filters by extension, and persists uploads to disk under UUID-prefixed filenames to prevent collisions, building a growing image pool the bot draws from at random.

---

## Commands

| Command | Arguments | Description |
|---|---|---|
| `!connor` | *message* (optional) | Mentions the target user with a random image from the pool. `!connor images` reports the current pool size. |
| `!weather` | *location* (default: Atlanta) | Current conditions and temperature via WeatherAPI. Distinguishes API errors from transport failures by status code. |
| `!cat` | `weight` \| `visits` \| `cycle` | Live sensor readings from Home Assistant: current pet weight with a relative last-updated timestamp, or today's litter box visit count. |
| `!fortnite` | *skin name* or `random` | Fetches the Fortnite cosmetics catalog, resolves the query by fuzzy match, and returns the skin's artwork, description, and introduction text. |
| `!sale` | *game title* | Searches CheapShark for matching titles, prompts for disambiguation via reactions, then returns the all-time lowest price and current deals resolved to store names. |
| `!timetil` | *age* (default: 30) | Countdown to a given birthday, broken into years/months/days/hours/minutes/seconds with correct singular and plural forms. |
| `!ip` | — | Returns the host's current public IP. |
| `!ow` | — | Random reaction GIF. |

---

## Architecture

```
ConnorBot
├── Discord layer      discord.py command handlers + event listeners
├── Integration layer  WeatherAPI · CheapShark · Fortnite API · Home Assistant · icanhazip
├── Media layer        UUID-namespaced attachment store, random selection
└── Config             environment-based secrets via python-dotenv
```

All credentials — bot token, Home Assistant URL and access token, weather API key — are loaded from environment variables at startup and never appear in source.

---

## Setup

**Requirements:** Python 3.11+

```bash
git clone https://github.com/daveydecker/ConnorBot.git
cd ConnorBot
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
BOT_TOKEN=your_discord_bot_token
HA_URL=http://your-home-assistant-host:8123/api
ACCESS_TOKEN=your_home_assistant_long_lived_token
WEATHER_TOKEN=your_weatherapi_key
```

Create the image storage directory the bot reads at startup:

```bash
mkdir images
```

Then run:

```bash
python ConnorBot.py
```

The bot requires the **Message Content** privileged intent, enabled in the Discord Developer Portal under your application's Bot settings.

---

## Configuration

A few values are currently hardcoded and should be moved to `.env` before deploying elsewhere:

- `CONNOR_ID` — the Discord user ID the bot mentions
- The image-ingestion channel ID in `on_message`
- `./images` — the attachment storage directory

---

## Roadmap

- [ ] Wire up `!cat cycle` to actually trigger the litter box vacuum service (the Home Assistant call is written but currently commented out; the command acknowledges without acting)
- [ ] Replace blocking `requests` calls with `aiohttp` so long API round-trips stop stalling the event loop
- [ ] Cache the Fortnite cosmetics catalog instead of refetching the full list on every invocation
- [ ] Write downloaded skin artwork to unique temp paths to avoid collisions between concurrent commands
- [ ] Move hardcoded IDs into configuration
- [ ] Add structured logging in place of bare `print` and broad `except` blocks

---

## Built With

`discord.py` · `homeassistant-api` · `requests` · `python-dotenv` · `python-dateutil` · `difflib` · `asyncio`
