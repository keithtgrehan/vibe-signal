# Physical iPhone QA - 2026-06-09

Status: Pending human run. Bundle ID is configured; no physical-device run has been performed in this report.

Required build:

- Bundle ID: `com.vibesignal.app`
- EAS profile: `qa`
- API URL: `https://vibe-signal.onrender.com`
- QA fixture mode: `closed_beta_synthetic`

EAS QA build command:

```bash
cd "/Users/keith/Documents/New project/vibe-signal/mobile"
npx eas build --platform ios --profile qa
```

Run instructions:

1. Confirm the build uses `com.vibesignal.app`.
2. Install the `qa` internal distribution build on a registered physical iPhone.
3. Use only built-in synthetic examples or attached synthetic QA fixtures.
4. Record device/build metadata and pass/fail results below.
5. Do not add screenshots or recordings unless they contain synthetic fixture content only.

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
