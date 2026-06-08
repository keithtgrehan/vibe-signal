# VibeSignal Local Backend

This backend exposes deterministic local routes for development and integration checks.

Run locally:

```bash
PYTHONPATH=src python -m uvicorn backend.app:app --reload --no-access-log
```

For Expo/mobile testing on another device, bind to the LAN interface:

```bash
PYTHONPATH=src python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 --no-access-log
```

Routes:

- `GET /healthz`
- `GET /readyz`
- `POST /api/analyze`
- `POST /api/match`
- `POST /api/feedback`
- `POST /api/events/analysis`
- `POST /api/events/quota`
- `POST /api/events/billing`
- `POST /api/events/state`
- `GET /legal/privacy`
- `GET /legal/terms`
- `GET /legal/data-deletion`
- `GET /legal/data-export`
- `GET /legal/match-disclaimer`

Safety boundaries:

- `/api/match` calls the deterministic matcher.
- Raw chats are not persisted by default.
- Request logs are metadata-only and include request ID, safe route template/category, status code, status category, latency bucket, and coarse error category.
- Unexpected backend exceptions return a generic error with a request ID instead of raw exception text.
- Feedback requires explicit consent.
- Feedback stores metadata only, not raw comment text.
- Event routes store bounded metadata only.
- Legal routes are static draft artifacts for closed-beta readiness and do not claim production compliance.
- Privacy, terms, deletion, export, and match disclaimer drafts require legal review before public launch.

Deployment readiness:

- See [docs/backend_deployment_readiness.md](../docs/backend_deployment_readiness.md).
- See [docs/ops/render_backend_runtime_requirements.md](../docs/ops/render_backend_runtime_requirements.md) for the minimal Render install and start commands.
- See [docs/deployment_smoke_tests.md](../docs/deployment_smoke_tests.md) for local/deployed backend smoke-test commands.
- See [deployment.env.example](deployment.env.example) for non-secret environment variable examples.
- `/readyz` reports route registration and hard safety flags; it is readiness metadata only and does not claim production compliance.
- CORS is opt-in through exact `VIBE_BACKEND_ALLOWED_ORIGINS`; wildcard origins are rejected by config parsing.
- Logs must stay metadata-only. Do not log raw chat text, request bodies, provider responses, credentials, model artifacts, vectors, or checkpoints.
- Disable or sanitize server/proxy access logs before handling beta traffic; the safe request logger is metadata-only, but default server access logs can include raw request lines.
- See [docs/monitoring_no_raw_logs.md](../docs/monitoring_no_raw_logs.md) for closed-beta monitoring checks, no-raw-log rules, and manual incident-response triggers.

Smoke-test the local backend before connecting mobile:

```bash
python scripts/smoke_test_deployed_backend.py --base-url http://127.0.0.1:8000
```

Mobile match integration:

```bash
cd mobile
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm start
```

Use `http://<your-machine-lan-ip>:8000` instead of `127.0.0.1` when testing from a physical phone. The mobile match card posts only the submitted exchange to `/api/match`; it does not store raw chat text locally or in the backend by default.

Match submission copy should tell users that Vibe Signal is communication-support only, outputs are pattern-based suggestions rather than truth claims, and users should not submit sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.
