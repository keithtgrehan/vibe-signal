# Backend Smoke Evidence

Date: 2026-06-03.

Backend: `https://vibe-signal.onrender.com`.

Status: passed after a warmed retry.

## Evidence Rules

Record command, pass/fail count, endpoint names, status codes, and request IDs only. Do not paste request bodies, response bodies, raw chats, headers, cookies, tester content, secrets, raw logs, raw external dataset rows, vectors, checkpoints, or model artifacts.

## Commands

```bash
PYENV_VERSION=3.11.3 python scripts/smoke_test_deployed_backend.py --base-url https://vibe-signal.onrender.com
PYENV_VERSION=3.11.3 python scripts/smoke_test_deployed_backend.py --base-url https://vibe-signal.onrender.com --include-events
curl -i -X OPTIONS "https://vibe-signal.onrender.com/api/match" -H "Origin: https://vibe-signal.vercel.app" -H "Access-Control-Request-Method: POST"
```

## Latest Run

The first concurrent smoke attempt on 2026-06-03 returned transient transport errors for early GET routes while later legal, analyze, match, feedback, and event routes passed. Direct warmed checks for `/healthz`, `/readyz`, `/legal/privacy`, and `/legal/terms` then returned 200 with safe request IDs.

Warmed retry summary:

- default smoke: `10/10` deployment smoke checks passed.
- event smoke: `14/14` deployment smoke checks passed.
- CORS preflight for `https://vibe-signal.vercel.app`: `HTTP/2 200` with `access-control-allow-origin: https://vibe-signal.vercel.app`.

No raw private content was used. Synthetic smoke payloads only.
