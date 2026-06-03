# Data Flow Summary

Status: implementation summary for legal/privacy review.

## Inputs

- synthetic demo messages
- user-provided messages only after consent gate
- bounded feedback labels after explicit consent
- metadata-only event payloads

## Backend Routes

- `/api/analyze`
- `/api/match`
- `/api/feedback`
- `/api/events/*`
- legal draft routes
- `/healthz`
- `/api/status`

## Storage Posture

- Raw message persistence is disabled by default.
- Raw message logging is disabled by default.
- Feedback stores ids, rating, comment length, consent state, and timestamps, not raw comments.
- Events store ids, route category, allowlisted monitoring type, timestamp, payload field count, and synthetic flag, not raw payloads.
- Evaluation data is synthetic-only.

## Third Parties

- Render hosts backend.
- Vercel hosts web frontend.
- Expo/TestFlight may be used for mobile beta distribution.
- Optional provider/BYOK code exists in the app; beta scope must be confirmed before use.
- No analytics SDKs are added by the release-gate work.

