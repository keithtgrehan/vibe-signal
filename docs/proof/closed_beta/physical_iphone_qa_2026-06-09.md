# Physical iPhone QA - 2026-06-09

Status: Pending human run.

Required build:

- EAS profile: `qa`
- API URL: `https://vibe-signal.onrender.com`
- QA fixture mode: `closed_beta_synthetic`

Required metadata:

- Tester:
- Device model:
- iOS version:
- Build number:
- EAS build ID:
- Git commit:
- Backend `/api/status` revision:

Pass/fail checklist:

- Install and launch:
- Consent gate before first private analysis:
- Empty input state:
- Synthetic happy path:
- Evidence/result mode:
- Match mode:
- Backend unreachable state, if available:
- Safety fallback:
- Feedback consent:
- App relaunch check:
- Keyboard/small-screen layout:
- No raw input in logs, debug output, screenshots outside app input/result flow, or feedback payloads:

Reject this report if it contains real/private/tester messages.
