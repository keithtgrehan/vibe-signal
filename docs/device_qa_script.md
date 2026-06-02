# Device QA Script

Status: closed-beta real-device QA script only. This does not prove production readiness, App Store readiness, legal compliance, GDPR/CCPA compliance, model quality, or commercial data rights.

Use synthetic toy messages only. Do not use real tester chats, third-party private messages, secrets, provider responses, credentials, medical data, legal documents, financial data, account data, phone numbers, emails, addresses, vectors, checkpoints, or model artifacts.

## Setup

1. Obtain the concrete backend host before starting.

   - Use the deployment tracker, hosting provider dashboard, or Replit deployment settings.
   - Record only a non-secret host label and git SHA in QA notes.
   - Do not guess the host from a workspace slug.
   - If no concrete backend host is available, mark deployed-device QA blocked.

2. Confirm backend smoke tests passed for the target host:

   ```bash
   python scripts/smoke_test_deployed_backend.py --base-url https://<your-backend-host>
   ```

3. If mobile event logging is enabled for this build, confirm event routes:

   ```bash
   python scripts/smoke_test_deployed_backend.py --base-url https://<your-backend-host> --include-events
   ```

4. Choose the beta distribution path before launch:

   - Expo Go/dev server for local QA.
   - Development build for native-module QA.
   - TestFlight build for iOS beta-distribution QA.

   For TestFlight or other native builds, confirm `EXPO_PUBLIC_API_URL` was set at build time. A shell env var changed after installation may not update an already-built app.

5. Start the mobile app with a clean backend base URL.

   Deployed backend:

   ```bash
   cd mobile
   EXPO_PUBLIC_API_URL=https://<your-backend-host> npm start -- --clear
   ```

   iOS simulator against a local backend:

   ```bash
   cd mobile
   EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm start -- --clear
   ```

   Android emulator against a local backend:

   ```bash
   cd mobile
   EXPO_PUBLIC_API_URL=http://10.0.2.2:8000 npm start -- --clear
   ```

   Physical phone against a local backend:

   From the repo root:

   ```bash
   ipconfig getifaddr en0 || ipconfig getifaddr en1
   PYTHONPATH=src python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 --no-access-log
   ```

   Confirm the phone is on the same network and can open `http://<your-machine-lan-ip>:8000/healthz` in its browser. Then start Expo:

   ```bash
   cd mobile
   EXPO_PUBLIC_API_URL=http://<your-machine-lan-ip>:8000 npm start -- --clear
   ```

6. Do not put route paths, query strings, fragments, usernames, passwords, tokens, or credentials in `EXPO_PUBLIC_API_URL`.

## Device Matrix

Run at least one pass on the actual beta distribution target. Mark unavailable paths as not run rather than inferred.

| Target | Required before beta? | Notes |
| --- | --- | --- |
| iOS physical device or TestFlight build | Yes for iOS beta | Confirms network, keyboard, safe-area, and store-environment behavior |
| iOS simulator | Useful but not sufficient | Good for layout and backend smoke, not App Store sandbox proof |
| Android emulator | Required only if Android beta is in scope | Use `10.0.2.2` for local backend |
| Android physical device | Required only if Android beta is in scope | Use deployed backend or machine LAN IP for local backend |

## App Start And Backend URL

1. Close the app and stop Metro.
2. Start app without `EXPO_PUBLIC_API_URL`:

   ```bash
   cd mobile
   env -u EXPO_PUBLIC_API_URL npm start -- --clear
   ```

   For a native/TestFlight build, reinstall or rebuild with the backend URL omitted if this state is in scope for the QA pass.

3. Confirm backend-bound flows fail safely or remain disabled.
4. Start app with a clean valid backend URL.
5. Confirm no screen displays the raw URL with secrets, paths, queries, fragments, or credentials.
6. Confirm backend verification or match request does not run until explicitly triggered by the user flow.

Pass criteria:

- Missing backend URL does not crash the app.
- Missing backend URL copy tells the operator to set `EXPO_PUBLIC_API_URL`.
- Invalid backend URL does not send network traffic; verify from visible app state plus absence of a new request ID in safe backend logs when a backend host is available.
- Error copy is user-facing and does not expose stack traces or raw backend traces.

## `/api/match` Happy Path

Use this synthetic input:

```text
self: Can you confirm Friday at 3pm?
other: Yes, Friday at 3pm works. No pressure if we need to adjust.
```

Steps:

1. Open the communication-fit or match screen.
2. Confirm consent/disclaimer copy is visible before submission.
3. Paste the synthetic input.
4. Submit once.
5. Observe loading state.
6. Confirm result state renders:
   - compatibility score or band
   - positive factors
   - risk factors, even if empty
   - evidence safe phrases
   - explanation or safe summary
7. Confirm output states that matching is based on observable communication patterns only.

Pass criteria:

- The request succeeds against the configured backend.
- The result contains only evidence-backed, cautious phrasing.
- No output claims truth, attraction, hidden intent, cheating, diagnosis, neurotype, attachment style, emotional truth, manipulation, or relationship success.

## Empty State

1. Open the match screen.
2. Leave the input blank.
3. Try to submit.

Pass criteria:

- The app does not send a request.
- The UI explains that a short exchange is needed without blaming the user.
- No raw debug details are shown.

## Loading State

1. Submit the happy-path synthetic input.
2. Observe the screen while the backend request is pending.

Pass criteria:

- Loading state is visible.
- The expected loading status text is `Checking communication fit...`.
- Submit controls do not create accidental duplicate sends.
- Existing consent/disclaimer copy remains reachable or previously visible.

## Error States

Use synthetic input for every error-state test. Do not use a real credential or secret in the URL.

Missing URL:

```bash
cd mobile
env -u EXPO_PUBLIC_API_URL npm start -- --clear
```

Invalid URL shape:

```bash
cd mobile
EXPO_PUBLIC_API_URL=https://example.invalid/path npm start -- --clear
```

Unreachable backend:

```bash
cd mobile
EXPO_PUBLIC_API_URL=https://unreachable.example.invalid npm start -- --clear
```

Backend non-OK or gateway failure:

- point the app at a controlled test host or temporary local route that returns a non-OK status.
- do not use a real third-party URL, credential, token, query string, or private payload.

Submit the synthetic happy-path input after each setup.

Pass criteria:

- The error is understandable.
- Missing or invalid URL, network unreachable, backend non-OK, and transport-unavailable states are handled without crashing.
- The error does not include stack traces, raw exception text, request bodies, response bodies, headers, cookies, credentials, provider responses, or private message text.
- The user can edit input or retry after fixing configuration.

## Consent, Legal, And Disclaimer Visibility

Check the build surfaces for:

- communication-support-only wording.
- pattern-based suggestions, not truth claims.
- permission warning for messages submitted for analysis.
- warning not to submit sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.
- privacy and terms links where required by the current mobile surface.
- match disclaimer route or copy when exposed.

Open the deployed legal draft routes or the app links that point to them:

- `/legal/privacy`
- `/legal/terms`
- `/legal/data-deletion`
- `/legal/data-export`
- `/legal/match-disclaimer`

Pass criteria:

- Copy is visible before or at the point of submission.
- Copy does not imply legal review is complete.
- Copy does not imply production launch.
- Draft legal routes are reachable when the build exposes legal links.
- Draft legal routes do not claim production compliance, GDPR/CCPA compliance, or final legal review.

## Event Logging Verification

Only run this section if `EXPO_PUBLIC_ENABLE_LOGGING` is intentionally enabled for the beta build.

From `mobile/`:

```bash
npm run verify:backend -- --api-url https://<your-backend-host> --event state
```

For a full route sweep:

```bash
npm run verify:backend -- --api-url https://<your-backend-host> --all
```

Pass criteria:

- Verifier prints only event type, target URL, status, payload field count, and response-body presence/length.
- Verifier does not print payload bodies, response bodies, private text, secrets, credentials, tokens, headers, or cookies.
- Event logging is non-blocking for user-facing analysis and match flows.

## TestFlight Or Store Sandbox Notes

Use this section only if the beta build includes subscription or paywall checks.

- Confirm StoreKit/RevenueCat product metadata loads in the target build.
- Confirm fallback catalog does not allow a purchase when live product metadata is unavailable.
- Confirm restore purchases does not crash.
- Do not use real payment credentials in repo notes.
- Do not call purchase success production-ready until sandbox purchase and restore are verified on device.

## Device QA No-Go Triggers

Pause tester invites, roll back, or rerun deployment smoke checks when any of these occur during device QA:

- deployed legal draft routes are unreachable or contradict the app copy.
- `/api/match` cannot be reached with the configured backend base URL.
- missing or invalid backend URL states attempt network requests.
- loading, empty, error, or result states crash or render raw debug details.
- user-facing output includes attraction, hidden intent, cheating, diagnosis, neurotype, attachment-style, emotional-truth, manipulation, or relationship-success claims.
- request IDs are missing from backend errors that need operator follow-up.
- screenshots, bug reports, logs, or QA notes contain private chats, secrets, credentials, provider responses, request bodies, response bodies, or real tester contact details.

## Recording Results

Record:

- date
- tester/operator initials
- git SHA
- mobile build label
- backend host label, not full secret-bearing URL
- device and OS
- pass/fail per section
- request IDs for backend issues
- coarse failure category

Do not record:

- private chats
- raw request or response bodies
- auth headers
- cookies
- credentials
- provider responses
- secrets
- real tester contact details
- model artifacts, vectors, checkpoints, or cached embeddings
