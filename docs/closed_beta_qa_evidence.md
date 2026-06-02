# Closed-Beta QA Evidence

This document records metadata-only closed-beta readiness evidence. Do not add raw chats, tester identities, request bodies, response bodies, screenshots containing private content, secrets, raw logs, provider responses, vectors, checkpoints, model files, or raw external dataset rows.

## Current Metadata

| Field | Status |
| --- | --- |
| Backend URL | `https://vibe-signal.onrender.com` |
| Hosted web frontend URL | `https://vibe-signal.vercel.app` |
| Backend platform | Render / FastAPI |
| Web platform | Vercel / Vite, root directory `web` |
| Backend default smoke | Passed: `10/10` using synthetic payloads |
| Backend event smoke | Passed: `14/14` using synthetic payloads |
| Hosted web CORS | Configured for exact Vercel origin |
| Local browser CORS | Requires exact localhost origins; no wildcard |
| Web QA | Hosted web reachable; synthetic `/api/match`, legal route, and CORS behavior verified by closed-beta audit |
| Mobile QA | Expo web/local tests covered; physical real-device QA remains pending |
| Legal URL status | Backend draft routes reachable; legal review remains pending |
| Incident owner | Keith |
| Monitoring source | Render logs/metrics plus Vercel deployment status |
| Alert path | Manual daily check during closed beta unless upgraded |
| Tester invites | Blocked until P0 gates pass |
| Production readiness | Not claimed |

## Evidence Rules

- Use synthetic toy examples only.
- Record command names, pass/fail summaries, route names, status codes, request IDs, coarse latency, build labels, and reviewer initials/roles only.
- Record CORS origins as exact origins only.
- Do not paste request or response bodies into this file.
- Do not include real tester data or private-message screenshots.

## Remaining Blockers

- Real-device iPhone QA is not complete.
- Legal/privacy/terms/deletion/export copy is draft and requires legal review.
- Manual monitoring cadence and backup owner need operational confirmation before tester invites.
- Tester invites remain blocked if hosted web CORS, legal routes, `/readyz`, or no-raw-log review regresses.

## P0 Triggers

- 5xx spike on beta routes.
- Legal draft route failure.
- CORS failure on `https://vibe-signal.vercel.app`.
- Any raw-message leakage suspicion.
- Unsafe output report.
- Raw request/response bodies, secrets, vectors, checkpoints, model files, or raw datasets in logs or artifacts.
