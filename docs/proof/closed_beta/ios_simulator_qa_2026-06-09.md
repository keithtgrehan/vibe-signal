# iOS Simulator QA - 2026-06-09

Status: Pending. Maestro scaffold exists; simulator run not performed in this report.

Synthetic-only command template:

```bash
cd "/Users/keith/Documents/New project/vibe-signal"
maestro test -e APP_ID="$APP_ID" --test-output-dir maestro/artifacts maestro
```

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
