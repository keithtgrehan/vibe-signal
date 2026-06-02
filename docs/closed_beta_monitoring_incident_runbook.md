# Closed-Beta Monitoring And Incident Runbook

## Ownership

| Field | Current value |
| --- | --- |
| Primary incident owner | Keith |
| Backup owner | Pending |
| Monitoring source | Render logs/metrics plus Vercel deployment status |
| Alert path | Manual daily check during closed beta unless upgraded |
| Support path | Pending reviewed support channel |

Do not commit personal phone numbers, private emails, credentials, dashboard secrets, raw logs, or tester identifiers.

## Daily Manual Check

Review metadata only:

- Render service health.
- Render 5xx/error rate.
- Render deployment status.
- Vercel deployment status for `https://vibe-signal.vercel.app`.
- `/healthz` and `/readyz`.
- Legal draft routes.
- CORS preflight from `https://vibe-signal.vercel.app`.
- Any reports of unsafe output or raw-message leakage.

## P0 Incident Triggers

- 5xx spike.
- Hosted web CORS failure.
- Legal route failure.
- `/readyz` reports raw message persistence, raw logging, analytics/tracking, or training enabled.
- Raw-message leakage suspicion.
- Unsafe output report.
- Raw request/response bodies, secrets, provider responses, vectors, checkpoints, model files, or raw datasets in logs or artifacts.

## Response

1. Disable tester invites.
2. Capture metadata-only incident notes: route, status code category, deployment label, timestamp, owner, and action taken.
3. Do not copy raw chats, request bodies, response bodies, raw logs, private screenshots, tester identifiers, or secrets.
4. If frontend-only, revert the Vercel deployment.
5. If backend behavior regressed, redeploy the previous Render backend commit.
6. Re-run backend smoke, event smoke, legal route checks, CORS preflight, and synthetic hosted-web `/api/match`.
7. Reopen tester invites only after the P0 condition is resolved and metadata-only evidence is recorded.

## Rollback Commands

Frontend rollback is performed through Vercel deployment history for the `web/` project.

Backend rollback is performed through Render by redeploying the previous known-good backend commit.

Use these validation commands after rollback:

```bash
export VIBE_BACKEND_HOST="https://vibe-signal.onrender.com"
python scripts/smoke_test_deployed_backend.py --base-url "$VIBE_BACKEND_HOST"
python scripts/smoke_test_deployed_backend.py --base-url "$VIBE_BACKEND_HOST" --include-events
curl -i -X OPTIONS "https://vibe-signal.onrender.com/api/match" \
  -H "Origin: https://vibe-signal.vercel.app" \
  -H "Access-Control-Request-Method: POST"
```
