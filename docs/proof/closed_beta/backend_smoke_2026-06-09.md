# Backend Smoke Proof - 2026-06-09

Status: Passed on deployed backend.

Target:

- Backend: `https://vibe-signal.onrender.com`

Command run:

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://vibe-signal.onrender.com --timeout 30 --retries 2
curl -fsS https://vibe-signal.onrender.com/api/status
```

Result:

- Summary: `10/10 deployment smoke checks passed`
- `/healthz`: pass, HTTP `200`
- `/readyz`: pass, HTTP `200`
- `/api/status`: pass, HTTP `200`; response reported `raw_message_persistence_enabled=false`, `raw_message_logging_enabled=false`, `analytics_tracking_enabled=false`, and `training_enabled=false`
- `/legal/privacy`: pass, HTTP `200`
- `/legal/terms`: pass, HTTP `200`
- `/legal/data-deletion`: pass, HTTP `200`
- `/legal/data-export`: pass, HTTP `200`
- `/legal/match-disclaimer`: pass, HTTP `200`
- `/api/analyze`: pass, HTTP `200`, synthetic payload only
- `/api/match`: pass, HTTP `200`, synthetic payload only
- `/api/feedback`: pass, HTTP `200`, synthetic feedback payload only

Required evidence covered:

- `/healthz`
- `/readyz`
- `/api/status`
- `/api/analyze` using synthetic text only
- `/api/match` using synthetic text only
- `/api/feedback` metadata-only consent path
- Legal route checks

Note: the smoke script does not currently include `/api/status`, so it was verified separately with `curl`.

Do not paste raw private chats, tester messages, or real screenshots into this report.
