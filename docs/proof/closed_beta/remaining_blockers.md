# Remaining Closed-Beta Blockers

Date: 2026-06-03.

## P0 Blockers

- Real-device iPhone/TestFlight QA has not been run.
- Legal/privacy review has not been completed.
- Production Render still returns a feedback comment hash on `/api/feedback`; this branch removes it, but deployed smoke remains partial until Render is redeployed after merge.
- App Store/TestFlight metadata has not been reviewed by counsel or the final accountable owner.

## P1 Follow-Ups

- Run hosted web manual QA against `https://vibe-signal.vercel.app` after this PR merges and deploys.
- Keep backend smoke proof current after any Render deployment.
- Add human-review labeling workflow before any future precision/recall or model-quality claim.

Tester invites remain `BLOCKED`.
