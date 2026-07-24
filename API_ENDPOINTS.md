# Lord Rush — Live API Surface

![endpoints 4](https://img.shields.io/badge/endpoints-4-57606a?style=flat-square)
![live 2](https://img.shields.io/badge/live-2-2ea44f?style=flat-square)
![removed 2](https://img.shields.io/badge/removed-2-cf222e?style=flat-square)
![scan read-only](https://img.shields.io/badge/scan-read--only-57606a?style=flat-square)

<sub>Backend `s01-gm-report-api-prod-eo.centurygame.com/api` &nbsp;·&nbsp; frontend `ls-giftcode.centurygame.com` &nbsp;·&nbsp; Vue SPA (game shown as "Lord Rush") &nbsp;·&nbsp; last scanned 24/07/2026 09:00 UTC</sub>

This document mirrors the gift-code API of **Lord Rush** exactly as the game's own public web client describes it — the endpoints its frontend calls, which of them the backend still answers, the request parameters, the encrypt key, and the signature scheme. It is produced by an automated scan that only reads Century Games' public JavaScript and probes their public API. We observe; we never modify the game's API, and never touch our own redemption keys.

---

## Endpoints

| Endpoint | Method | Backend | Payload keys[¹](#reading-the-payload-keys) |
|---|:--:|:--:|---|
| `/gift_code` | `POST` | ![live](https://img.shields.io/badge/live-2ea44f?style=flat-square) | `cdk` `fid` `kid` `sign` `time` |
| `/gift_code_config` | `POST` | ![live](https://img.shields.io/badge/live-2ea44f?style=flat-square) | — |
| `/captcha` | `POST` | ![removed](https://img.shields.io/badge/removed-cf222e?style=flat-square) | — |
| `/player` | `POST` | ![removed](https://img.shields.io/badge/removed-cf222e?style=flat-square) | — |

<sub>**Backend** is probed with a deliberately invalid, side-effect-free body and classified purely on HTTP status — `live` = the host answered (any 2xx/4xx other than 404), `removed` = the host returns 404. The **Method** column is the verb the frontend uses; the liveness probe always POSTs, and a 404 comes back regardless of verb, so it cleanly proves removal.</sub>

> [!IMPORTANT]
> **Lord Rush redeems in a single signed call.** Unlike the older captcha-and-login flow, redemption here is **one** signed `POST /gift_code` — there is **no** player-login step and **no** captcha. Century Games never shipped (or has since dropped) the `/player` and `/captcha` routes for this game; both now answer 404, mirroring the same removal on Century's other titles. Each removal is dated in the [change timeline](API_DATAMINING.md).

<details>
<summary><b>Verify it yourself</b> — read-only, one status probe per path</summary>

The body redeems nothing (invalid `fid`/`time`); only the HTTP status is read.

```bash
for p in gift_code gift_code_config captcha player; do
  code=$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST "https://s01-gm-report-api-prod-eo.centurygame.com/api/$p" -d 'fid=0&time=0')
  echo "$code  /$p"
done
# expect: 200 /gift_code · 200 /gift_code_config · 404 /captcha · 404 /player
```

</details>

---

## Signature scheme

```
sign = MD5("cdk={cdk}&fid={fid}&kid={kid}&time={time}" + ENCRYPT_KEY)
params alphabetical (cdk · fid · kid · time); time in unix SECONDS; kid required; no captcha, no login step. (Century Games' own scheme, visible in their public JS.)
```

Every request to `/gift_code` carries `sign, fid, cdk, kid, time`. The signed string is the four request params in **alphabetical order** joined with `&`, followed by the encrypt key below, hashed with MD5. `kid` (the kingdom id) is **required** — the backend rejects a redemption whose `kid` does not match the account. It is Century Games' own scheme, extracted from their public gift-code client and reproduced here for transparency **(last verified 24/07/2026)**.

---

## Encrypt key

```
ZUk4FG1VQq3HjPKAa
```

Century Games' own per-game key, extracted from their **public** gift-code JavaScript. It is published here on purpose: the whole point of this doc is transparency, so anyone can reproduce a valid `/gift_code` request from the scheme above plus this key against Century's public API. The scanner only *reads* it from the public bundle — it never writes it back into our own redemption config.

---

## Reading the payload keys

Payload keys are extracted as **one set per bundle chunk, not per endpoint**. The client is minified, which erases the link between a request parameter and the exact endpoint that sends it. We therefore report the chunk-wide key set and attach it to the one live signing endpoint (`/gift_code`). Read-only config reads (`/gift_code_config`) carry no signed payload and show `—`; the two `removed` paths answer 404 and expose no observable payload, so they show `—` as well. Methods are inferred from the bundle by a substring heuristic and re-checked on change.

---

## Error codes

![codes 4](https://img.shields.io/badge/codes-4-57606a?style=flat-square)
![flow signed single-call](https://img.shields.io/badge/flow-signed%20single--call-2ea44f?style=flat-square)
![source observed](https://img.shields.io/badge/source-observed-57606a?style=flat-square)

How **Lord Rush**'s gift-code backend replies, and what our redeemer does with each reply. These are **our own observations** of Century Games' `err_code` values — read off our redemption handler, **not** produced by the scanner — so this table is hand-maintained. `terminal` = we stop; `needs review` = we stop and never delete anything, a human corrects it.

| `err_code` | Our label | Handling | What it means |
|---|---|:--:|---|
| `20000` | SUCCESS | ![success](https://img.shields.io/badge/success-2ea44f?style=flat-square) | Code redeemed for this player. We mark the player's kingdom verified and stop. |
| `40008` | ALREADY_USED | ![terminal](https://img.shields.io/badge/terminal-57606a?style=flat-square) | This player has already claimed this code. Treated as done, not an error. |
| `40014` | CDK_NOT_FOUND | ![terminal](https://img.shields.io/badge/terminal-57606a?style=flat-square) | The code does not exist / is invalid; we mark the code `invalid`. |
| `40020` | KID_MISMATCH | ![needs review](https://img.shields.io/badge/needs%20review-cf222e?style=flat-square) | The `kid` (kingdom id) we sent does not match this player's actual kingdom (e.g. they moved kingdoms), OR the player id does not exist — the API cannot tell those apart. We never retry it and never delete the player; a human corrects the kingdom. |

> [!NOTE]
> Century Games may occasionally return additional transient replies (short-lived per-account throttles or backend hiccups). Those are **not** rejections — we back off and retry them. They must never be confused with `40020` (`KID_MISMATCH`), which is a stable, per-account condition that a retry cannot fix.

<sub>Handling is what **our** redeemer does; the `err_code` numbers and their meanings belong to Century Games. We observe and react — we never change the game's responses.</sub>

---

## Rate limits

![game throttle transient](https://img.shields.io/badge/game%20throttle-transient-bf8700?style=flat-square)
![fixed rps none](https://img.shields.io/badge/fixed%20rps-none-57606a?style=flat-square)

The `/gift_code` endpoint carries **no fixed requests-per-second limit** we have observed. Because redemption is a single signed call per `(fid, kid)`, throughput scales with how many accounts we process rather than with a per-endpoint cap. Any transient throttle Century Games applies is handled by back-off-and-retry (see [Error codes](#error-codes)).

---

## Scope

The scanner is read-and-report only. It writes to two database tables and to these public documents — never to `api_keys.json`, `config.py`, or the redeem path. The full change history lives in the append-only [change timeline](API_DATAMINING.md).

<sub>Generated from Century Games' public gift-code client · Lord Rush · scan is read-only · published for transparency.</sub>
