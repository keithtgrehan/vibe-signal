# Vibe Signal Maestro Smoke Suite

Run these flows only against synthetic QA builds.

Prerequisites:

- Build or launch the Expo app with `EXPO_PUBLIC_QA_FIXTURE_MODE=closed_beta_synthetic`.
- Provide the installed app id through `APP_ID`.
- Use synthetic fixture text only.

Example:

```bash
cd "/Users/keith/Documents/New project/vibe-signal/mobile"
EXPO_PUBLIC_API_URL=https://vibe-signal.onrender.com EXPO_PUBLIC_QA_FIXTURE_MODE=closed_beta_synthetic npm start -- --clear

cd "/Users/keith/Documents/New project/vibe-signal"
maestro test -e APP_ID="$APP_ID" --test-output-dir maestro/artifacts maestro
```

`03_backend_unreachable.yaml` requires a separate QA build or local launch with an unreachable API URL.
