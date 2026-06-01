# VibeSignal Local Backend

This backend exposes deterministic local routes for development and integration checks.

Run locally:

```bash
uvicorn backend.app:app --reload
```

Routes:

- `GET /healthz`
- `POST /api/analyze`
- `POST /api/match`
- `POST /api/feedback`
- `POST /api/events/analysis`
- `POST /api/events/quota`
- `POST /api/events/billing`
- `POST /api/events/state`

Safety boundaries:

- `/api/match` calls the deterministic matcher.
- Raw chats are not persisted by default.
- Feedback requires explicit consent.
- Feedback stores metadata only, not raw comment text.
- Event routes store bounded metadata only.
