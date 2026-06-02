# VibeSignal Local Backend

This backend exposes deterministic local routes for development and integration checks.

Run locally:

```bash
uvicorn backend.app:app --reload
```

For Expo/mobile testing on another device, bind to the LAN interface:

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
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
- `GET /legal/privacy`
- `GET /legal/terms`
- `GET /legal/data-deletion`
- `GET /legal/data-export`
- `GET /legal/match-disclaimer`

Safety boundaries:

- `/api/match` calls the deterministic matcher.
- Raw chats are not persisted by default.
- Feedback requires explicit consent.
- Feedback stores metadata only, not raw comment text.
- Event routes store bounded metadata only.
- Legal routes are static draft artifacts for closed-beta readiness and do not claim production compliance.
- Privacy, terms, deletion, export, and match disclaimer drafts require legal review before public launch.

Mobile match integration:

```bash
cd mobile
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm start
```

Use `http://<your-machine-lan-ip>:8000` instead of `127.0.0.1` when testing from a physical phone. The mobile match card posts only the submitted exchange to `/api/match`; it does not store raw chat text locally or in the backend by default.

Match submission copy should tell users that Vibe Signal is communication-support only, outputs are pattern-based suggestions rather than truth claims, and users should not submit sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.
