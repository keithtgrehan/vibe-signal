# iOS Incident And Rollback Plan

Primary incident owner: Keith.

Backup owner: pending before tester invites.

## Monitoring Sources

- Render logs/metrics for backend health.
- Vercel deployment status for hosted web.
- Expo/EAS build status for mobile distribution.
- Manual daily check during closed beta unless upgraded.

## P0 Triggers

- 5xx spike.
- Legal route failure.
- CORS failure on the hosted web origin.
- Raw-message leakage suspicion.
- Unsafe output report.
- App build points at the wrong backend.
- Feedback, support, deletion, or export copy contradicts actual behavior.

## Immediate Actions

1. Pause tester invites.
2. Collect only metadata: route, status code, request ID, build label, coarse error category, timestamp.
3. Do not copy tester messages into incident notes.
4. Roll back Vercel frontend if web is affected.
5. Redeploy previous Render backend commit if backend is affected.
6. Pull or supersede the affected mobile build if iOS is affected.
7. Rerun smoke, CORS, no-raw-log, and device QA before resuming invites.
