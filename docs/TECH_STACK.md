---
title: Lords Rush Bot Technical Architecture - Python, PostgreSQL, Telegram, Discord
description: Technical documentation for Lords Rush Bot covering system architecture, tech stack, signed gift-code redemption, database schema, and API integration
keywords: lords rush bot architecture, python telegram bot, discord bot, postgresql, async python, lords rush api, century games bot, lords rush gift code api
---

# ⚔️ Lords Rush Bot — Technical Architecture

## System Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    Lords Rush Bot Server                      │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Telegram    │  │   Discord    │  │   Background Tasks   │ │
│  │  Bot API     │  │   Bot API   │  │                      │ │
│  │  (PTB v21)   │  │  (dpy v2)   │  │  • Gift Code Loop   │ │
│  │              │  │              │  │  • Retry Queue       │ │
│  │  Commands    │  │  Slash Cmds  │  │  • Premium Expiry    │ │
│  │  Callbacks   │  │  Events     │  │  • Leaderboard       │ │
│  └──────┬───────┘  └──────┬──────┘  └──────────┬───────────┘ │
│         │                 │                     │             │
│         └────────────┬────┴─────────────────────┘             │
│                      │                                        │
│              ┌───────▼────────┐                               │
│              │   PostgreSQL   │                               │
│              │   Database     │                               │
│              └────────────────┘                               │
└───────────────────────────────────────────────────────────────┘
```

## Lords Rush-Specific Architecture

### Gift Code Redemption
Lords Rush redeems in a **single signed call** — there is no player-login step and no captcha.

| Property | Value |
|----------|-------|
| Endpoint | `POST https://s01-gm-report-api-prod-eo.centurygame.com/api/gift_code` |
| Params | `sign, fid, cdk, kid, time` |
| Signature | `sign = md5(sorted params + a per-game secret key)` |
| Timestamp | unix **seconds** |
| Kingdom | `kid` **required** |
| Captcha | none |
| Login | none |

The signing key is a **per-game secret** and is **never** committed to this public repo — only the scheme is documented. See [API_ENDPOINTS.md](../API_ENDPOINTS.md) for the live surface and error codes.

### API Integration
The bot communicates with Century Games' official Lords Rush APIs:

| Function | Description |
|----------|------------|
| Gift Code Redemption | Redeem codes per `(fid, kid)` via `/gift_code` |
| Banner / Config | Read gift-code banners via `/gift_code_config` |
| Request Signing | MD5-based signature over sorted params + secret key |

> ℹ️ Lords Rush exposes **no** player-info endpoint — `POST /api/player` and `POST /api/captcha` return 404 (removed by Century Games). The bot therefore redeems against the FID + kingdom supplied at registration, without a separate lookup.

## Core Technologies

### Python 3.13+
- **Async/await** throughout the entire codebase
- `asyncio` for concurrent task management
- Thread executors for synchronous library integration

### python-telegram-bot v21
- Async-native Telegram Bot API wrapper
- `ConversationHandler` for multi-step flows (registration, alliance setup)
- `InlineKeyboardMarkup` for interactive menus
- HTML parse mode for rich message formatting

### discord.py v2.x
- Slash command integration (`app_commands`)
- `discord.Embed` for rich message display
- Cross-thread communication with `run_coroutine_threadsafe`

### PostgreSQL 15+
- Primary data store for all bot data
- Composite primary keys: `(fid, game_type)`
- `game_type` column on all relevant tables (`'lr'`)
- `ON CONFLICT` upserts for idempotent operations

### aiohttp
- Async HTTP client for game API calls
- Concurrent redemptions with `asyncio.gather`

## Module Architecture

```
lords-rush-bot/
├── bot.py                  # Main entry, handlers, dual-bot startup
├── config.py               # API hosts, tokens, secrets (not committed)
├── shared_state.py         # Cross-module bot references
├── modules/
│   ├── common.py           # Shared utils, game configs
│   ├── registration.py     # /register, FID + kingdom capture
│   ├── members.py          # /addmember, /members, /export
│   ├── alliance.py         # /setupalliance, /alliance
│   ├── giftcode.py         # Code discovery, validation, signed redemption
│   ├── leaderboard.py      # /leaderboard rankings
│   └── premium.py          # Subscription limits & expiry
├── locales/
│   ├── en.json             # English
│   ├── ja.json             # Japanese
│   ├── ko.json             # Korean
│   ├── ru.json             # Russian
│   └── tr.json             # Turkish
└── db/
    └── migrate_game_type.py
```

## Key Design Decisions

### Game-Type Aware Database
Every table includes a `game_type` column (`'lr'` for Lords Rush):
- Single database serves multiple games on the same platform
- Composite primary keys prevent FID collisions across games
- Queries are always scoped by `game_type`
- Gift codes are game-specific

### Single Process, Dual Bot
Both Telegram and Discord bots run in the same Python process:
- Telegram uses the main `asyncio` event loop
- Discord runs in a separate thread
- `shared_state.py` bridges between them

### Locale System
- JSON-based locale files (EN/JA/KO/RU/TR)
- `get_text(key, lang)` for string retrieval
- Per-group language settings
- Fallback to English if key missing

## External APIs

| API | Purpose | Auth | Status |
|-----|---------|------|--------|
| Lords Rush Gift Code API (`/gift_code`) | Redemption | Sign + FID + kid | ✅ live |
| Lords Rush Config API (`/gift_code_config`) | Banners | — | ✅ live |
| Lords Rush Player API (`/player`) | Player info | — | ❌ removed (404) |
| Lords Rush Captcha API (`/captcha`) | Captcha | — | ❌ removed (404) |

> The platform also ships a local ONNX captcha solver used by other Century Games titles; **Lords Rush redemption needs no captcha**, so it is not used for this game.
