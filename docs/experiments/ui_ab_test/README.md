# Vibe Signal UI A/B Test Governance

Production is the Vercel deployment from `main`:

- URL: `https://vibe-signal.vercel.app`
- Backend: `https://vibe-signal.onrender.com`

Replit is an experimental friend-feedback environment:

- URL: `https://vibe-signal-ab.replit.app`
- Target branch: `replit/ab-minimal-frontend-redesign`
- Backend: `https://vibe-signal.onrender.com`

Both variants use the same Render backend. Replit must not be merged into `main` until `decision_template.md` is completed after friend feedback.

Feedback must use synthetic examples or text the tester has permission to analyze. Do not collect real private chats from friends.

No analytics, tracking SDKs, auth, raw message storage, raw message logging, backend changes, API contract changes, or production n8n wiring should be added for this experiment.
