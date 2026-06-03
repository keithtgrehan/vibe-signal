# TestFlight Launch Runbook

Status: configuration and QA runbook only. This does not approve App Store review, TestFlight distribution, legal compliance, production readiness, or tester invites.

## Current Configuration

- Expo project root: `mobile/`
- Backend env var: `EXPO_PUBLIC_API_URL`
- Production backend value for beta builds: `https://vibe-signal.onrender.com`
- EAS config: `mobile/eas.json`
- Local env template: `mobile/.env.example`

The current `mobile/app.json` does not set an iOS bundle identifier. Keep it that way until Keith confirms the App Store Connect bundle ID. EAS can prompt for it during first build setup, but the confirmed value should be reviewed before commit.

## Preflight

1. Confirm PR branch SHA and intended beta build label.
2. Confirm legal/privacy/terms/deletion/export drafts remain visible and legally reviewed or explicitly blocked.
3. Confirm `EXPO_PUBLIC_API_URL` is a base URL only, with no path, query, fragment, token, username, password, or secret.
4. Confirm no analytics/tracking SDK was added.
5. Run `cd mobile && npm test`.
6. Run `cd mobile && npx expo config --type public`.

## Development Build

```bash
cd mobile
EXPO_PUBLIC_API_URL=https://vibe-signal.onrender.com npx expo config --type public
eas build --platform ios --profile development
```

Only run the EAS build when Apple/Expo credentials are configured locally. If credentials are missing, record that as a blocker rather than changing app behavior.

## Preview/Internal Build

```bash
cd mobile
eas build --platform ios --profile preview
```

Use internal distribution only after synthetic backend smoke, legal-route checks, and no-raw-log review are complete.

## Production/TestFlight Build

```bash
cd mobile
eas build --platform ios --profile production
```

Do not submit or invite testers until real-device QA, legal review, incident ownership, and launch gates pass.

## Blockers Before Tester Invites

- Confirmed iOS bundle identifier and App Store Connect setup.
- EAS credentials available and reviewed.
- Real-device iPhone QA completed on the intended build.
- Legal review completed for privacy, terms, deletion, export, support, and disclaimer copy.
- Incident owner and backup owner recorded.
- Metadata-only monitoring path confirmed.
