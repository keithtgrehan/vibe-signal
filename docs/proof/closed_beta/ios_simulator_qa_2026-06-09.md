# iOS Simulator QA - 2026-06-09

Status: Pending. Bundle ID is configured and Maestro scaffold exists; simulator run not performed in this report.

Bundle ID:

- `com.vibesignal.app`

Synthetic-only command template:

```bash
cd "/Users/keith/Documents/New project/vibe-signal/mobile"
npx eas build --platform ios --profile preview
cd "/Users/keith/Documents/New project/vibe-signal"
maestro test -e APP_ID="$APP_ID" --test-output-dir maestro/artifacts maestro
```

Command plan:

1. Build or launch an iOS simulator app using the synthetic QA fixture profile.
2. Confirm `EXPO_PUBLIC_QA_FIXTURE_MODE=closed_beta_synthetic`.
3. Run the Maestro suite against the simulator app ID.
4. Store screenshots, logs, and Maestro output under `maestro/artifacts/`.
5. Update this report only after the simulator run is actually performed.

Required metadata:

- Git commit:
- EAS/profile or Expo launch mode:
- Simulator model:
- iOS version:
- API URL:
- QA fixture mode:

Required flows:

- Launch
- Empty input
- Synthetic happy path
- Backend unreachable, if configured
- Consent gate
- Safety fallback
- Match mode
- Evidence card

Artifact rule: screenshots, recordings, and logs must contain synthetic fixture text only.

Do not treat this report as simulator proof until Maestro has actually run.
