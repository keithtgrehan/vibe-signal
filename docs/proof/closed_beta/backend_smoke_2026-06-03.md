# Backend Smoke Evidence

Date: 2026-06-03.

Backend: `https://vibe-signal.onrender.com`.

Status: `PARTIAL` after RC hardening added a stricter feedback privacy check.

## Evidence Rules

Record command, pass/fail count, endpoint names, status codes, and request IDs only. Do not paste request bodies, response bodies, raw chats, headers, cookies, tester content, secrets, raw logs, raw external dataset rows, vectors, checkpoints, or model artifacts.

## Commands

```bash
PYENV_VERSION=3.11.3 python scripts/smoke_test_deployed_backend.py --base-url https://vibe-signal.onrender.com --retries 3 --retry-delay-seconds 2
PYENV_VERSION=3.11.3 python scripts/smoke_test_deployed_backend.py --base-url https://vibe-signal.onrender.com --include-events --retries 3 --retry-delay-seconds 2
curl -i -X OPTIONS "https://vibe-signal.onrender.com/api/match" -H "Origin: https://vibe-signal.vercel.app" -H "Access-Control-Request-Method: POST"
```

## Latest Run

PR #19 previously passed default `10/10` and event `14/14` after a warmed retry. This RC hardening branch adds a stricter feedback privacy check that fails if `/api/feedback` returns a feedback comment hash field.

Current hardened smoke summary:

- default smoke: `9/10` deployment smoke checks passed.
- event smoke: `13/14` deployment smoke checks passed.
- only failing endpoint: `POST /api/feedback`, detail `feedback_comment_hash_returned`.
- CORS preflight for `https://vibe-signal.vercel.app`: `HTTP/2 200` with `access-control-allow-origin: https://vibe-signal.vercel.app`.

The branch code removes feedback comment hashing from backend storage and hardens route tests. Production Render still needs redeploy after merge to clear the deployed smoke failure. No raw private content was used. Synthetic smoke payloads only.
