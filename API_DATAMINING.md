# Lord Rush — API Change Timeline

![log append-only](https://img.shields.io/badge/log-append--only-57606a?style=flat-square)
![last change 24/07/2026](https://img.shields.io/badge/last%20change-24%2F07%2F2026-2ea44f?style=flat-square)

An **append-only** record of every change we observe in Lord Rush's gift-code API. Entries are only ever added — nothing is edited or deleted — so a removed endpoint or a retired payload shape keeps its row here permanently. Newest first.

> [!IMPORTANT]
> **Append-only guarantee.** No row is ever removed from this log. When the backend drops an endpoint or the frontend changes a payload, we add a new line; we never rewrite history. The git commit trail of this file is itself part of the record.

**Change types** — ![added](https://img.shields.io/badge/added-2ea44f?style=flat-square) new endpoint or parameter &nbsp;·&nbsp; ![changed](https://img.shields.io/badge/changed-bf8700?style=flat-square) method or payload changed &nbsp;·&nbsp; ![removed](https://img.shields.io/badge/removed-cf222e?style=flat-square) backend stopped answering (404)

---

| Date (UTC) | Endpoint | Change | Detail |
|---|---|:--:|---|
| 24/07/2026 09:00 | `/gift_code` | ![added](https://img.shields.io/badge/added-2ea44f?style=flat-square) | Lord Rush gift-code API mapped — single signed `POST`, params `sign, fid, cdk, kid, time`, `sign = md5(sorted params + per-game secret key)`, unix-**seconds** timestamp, `kid` required, **no captcha**, **no login step** |
| 24/07/2026 09:00 | `/gift_code_config` | ![added](https://img.shields.io/badge/added-2ea44f?style=flat-square) | banner/config endpoint live (read-only, no signed payload) |
| 24/07/2026 09:00 | `/captcha` | ![removed](https://img.shields.io/badge/removed-cf222e?style=flat-square) | backend returns 404 — Century Games API (removed, mirroring WOS/KS 2026-07-21) |
| 24/07/2026 09:00 | `/player` | ![removed](https://img.shields.io/badge/removed-cf222e?style=flat-square) | backend returns 404 — Century Games API (removed, mirroring WOS/KS 2026-07-21) |

> **2026-07-24 — baseline mapping.** Lord Rush gift-code API mapped: `/api/gift_code` + `/api/gift_code_config` live; `/api/player` + `/api/captcha` return 404 (removed, mirroring WOS/KS 2026-07-21); single signed `POST`, `kid` required, seconds timestamp, no captcha.

<sub>The oldest rows are the **seeded baseline** — the known state captured when scanning began (the backend had already dropped `/player` and `/captcha`, and redemption was already the single signed call). Every row after the baseline is appended automatically by the daily scan.</sub>

## Notes

> [!NOTE]
> Payload changes are detected against a **per-bundle key set**, not per endpoint: minification hides which key belongs to which endpoint, so a payload delta reflects the whole chunk. Backend removals are recorded even though the affected paths may remain **referenced by the frontend** — that gap is exactly what this log exists to make visible.

See the current surface and signature scheme (signing key included) in **[API_ENDPOINTS.md](API_ENDPOINTS.md)**.

<sub>Datamined from Century Games' public gift-code client · Lord Rush · read-only, append-only.</sub>
