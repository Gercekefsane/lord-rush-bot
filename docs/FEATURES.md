---
title: Lord Rush Bot Features - Gift Code Redemption, Alliance Management
description: Complete feature documentation for Lord Rush Bot including automatic gift code redemption, kingdom-aware signed requests, alliance member management, leaderboard, and multi-language support
keywords: lords rush bot features, lords rush gift code bot, automatic gift code redemption, lords rush alliance management, kingdom, telegram bot, discord bot, century games bot, lords rush coupon bot
---

# ⚔️ Lord Rush Bot — Feature Details

## 🎁 Gift Code System

### How Auto-Discovery Works
1. The bot scans for new **Lord Rush** gift codes every **5 minutes**
2. New codes are stored in PostgreSQL with `pending` status
3. Each code is validated against the official gift-code API
4. Codes are automatically redeemed for **every registered member**
5. Notifications are sent and pinned in alliance groups

### Code Lifecycle
```
Discovered → Pending → Validated → Auto-Used → Expired/Invalid
```

### Lord Rush Redemption API
The bot uses Century Games' official gift-code API for Lord Rush:
- **Single signed request** — one `POST /gift_code` per account (`sign, fid, cdk, kid, time`)
- **Signature scheme** — `sign = md5(sorted params + a per-game secret key)`, timestamp in unix **seconds**
- **Kingdom-aware** — `kid` (kingdom id) is **required** on every redemption
- **No captcha, no login step** — the `/player` and `/captcha` routes were removed by Century Games (they answer 404)
- **Per-member tracking** — every redemption result is recorded per member per code

### Smart Retry System
- Transient failures are queued for retry
- Exponential backoff avoids hammering the endpoint
- Maximum retry attempts configurable
- Detailed error tracking per member per code (see the `err_code` table in [API_ENDPOINTS.md](../API_ENDPOINTS.md))

---

## 👥 Member Management

### Registration
Because Lord Rush redeems codes **per kingdom** and exposes **no player-info endpoint**, registration collects the two things the redeemer needs:
1. **FID** — the player's Fighter ID
2. **Kingdom** — the kingdom number (`kid`) the codes should be redeemed against

### Registration Methods
1. **Command**: `/register 123456789` — direct FID registration (then set your kingdom)
2. **Admin Add**: `/addmember 123456789 TAG` — admin registers on behalf of a member

### What Gets Stored
| Field | Description |
|-------|-------------|
| **FID** | The player's Fighter ID (redemption target) |
| **Kingdom** | The kingdom id (`kid`) required by the redeem call |
| **Alliance** | The alliance the member belongs to in the bot |

> ℹ️ Lord Rush has no public player-info API (the `/player` route returns 404), so the bot does not fetch or track in-game nickname changes for this game — it stores the FID and kingdom you provide and redeems against them.

---

## 🏆 Leaderboard

The `/leaderboard` command ranks alliances and members by real activity:
- **Top Alliances** — by total codes redeemed and active members
- **Top Members** — most codes redeemed within an alliance
- **Podium, tiers & badges** — presented on woscontrol.com/leaderboard
- **Cross-platform** — one shared ranking across Telegram and Discord

---

## 🌐 Multi-Language Support

### Supported Languages
| Language | Code | Coverage |
|----------|------|----------|
| English | `en` | 100% |
| 日本語 | `ja` | 100% |
| 한국어 | `ko` | 100% |
| Русский | `ru` | 100% |
| Türkçe | `tr` | 100% |

### How It Works
- Each group/user can set their preferred language
- All bot messages, buttons, and notifications are localized
- Language can be changed with `/language`
- Falls back to English for any missing key

---

## 🔄 Cross-Platform

### Telegram Features
- Inline keyboards for navigation
- HTML-formatted messages
- Group and private chat support
- Message pinning for gift code notifications

### Discord Features
- Slash commands (`/register`, `/help`, etc.)
- Embed messages with rich formatting
- Server and channel-based alliance linking
- Message pinning for gift code alerts
