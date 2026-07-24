# Changelog

All notable changes to this project are documented here.

## v1.0.0 — 2026-07-24

### ✨ Added
- **Lords Rush Support**: Full support for **Lords Rush** (Century Games) added to the bot platform, running 24/7 on both Telegram and Discord with a shared database
- **Automatic Gift Code Redemption**: New gift codes are discovered, validated, and redeemed for every registered member automatically — a single signed `POST /gift_code` per account, kingdom-aware (`kid`), with **no captcha and no login step**
- **`/register [FID]`**: Members register with their Fighter ID (FID); because Lords Rush codes are redeemed per kingdom, registration collects your **kingdom number** up front so codes always reach the right account
- **Gift Code Listing & Manual Redeem**: `/codes` lists every known code and its status; admins can add (`/addcode`) or redeem (`/usecode`) codes for the whole alliance on demand
- **Alliance Management**: Create and manage alliances with guided setup, member add/remove, member export, and per-group linking on both platforms
- **Leaderboard**: `/leaderboard` ranks alliances and members by codes redeemed and activity, with a podium and tier badges on the website
- **Premium & Subscription System**: Tiered plans with configurable member limits, expiry warnings (7/3/1 day), and a grace period after expiry
- **Five Languages**: English, 日本語, 한국어, Русский, and Türkçe — per-group language configuration with fallback to English
- **Website Integration**: Live Lords Rush gift codes are published to [woscontrol.com/codes](https://woscontrol.com/codes), auto-updated every 5 minutes

### 🔧 Fixed
- **Kingdom-Aware Redemption**: Redemptions now always send the correct `kid`, so codes stop failing with a kingdom mismatch and land on the right account the first time
- **Case-Sensitive Codes**: Codes now keep the exact upper- and lower-case you type, so case-sensitive codes redeem correctly

### 🔄 Changed
- **Single Signed Redemption Flow**: Lords Rush redemption is a single signed call (`sign = md5(sorted params + a per-game secret key)`, unix-seconds timestamp) — no player-info lookup and no captcha step, matching Century Games' current backend for this game
- **Game-Type Awareness**: All operations are scoped by game type (`lr`) so Lords Rush alliances only ever see Lords Rush codes

---
