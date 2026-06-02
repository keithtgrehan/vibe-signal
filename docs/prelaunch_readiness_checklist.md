# Prelaunch Readiness Checklist

This checklist is an honest split between code-complete work, still-manual configuration, and real-device validation that has not yet happened in this repo.

## Done

- mobile quota engine is implemented
- premium unlocking path uses the Apple App Store billing path in code
- restore purchases surface exists in the mobile UI
- a non-blocking upgrade prompt can appear after repeated successful analyses before the hard limit
- fallback catalog purchases are blocked safely
- premium entitlement truth comes from the named entitlement path
- mobile event logging queue is bounded
- event dedupe is implemented
- event sequence numbers persist locally
- event payloads are validated before send
- malformed payloads are dropped safely
- state logging is diff-aware and debounced
- telemetry is fire-and-forget and non-blocking
- secure installation identity is fail-closed
- secure provider credential storage is fail-closed
- recent local analysis history is capped and persisted locally
- privacy and terms link support now exists in config and UI wiring
- purchase and restore failure states are bounded and non-crashing
- backend `/readyz` readiness metadata exists
- backend CORS config is exact-origin and environment-driven
- backend request logs are metadata-only and carry request IDs
- backend unexpected-error responses are generic and include request IDs
- backend deployment smoke-test script exists for liveness, readiness, legal draft routes, and synthetic `/api/match`
- closed-beta readiness, tester instruction, and real-device QA documents exist

## Code-complete but unverified on real device

- RevenueCat product lookup with live App Store sandbox data
- successful sandbox purchase
- restore purchases after reinstall
- mobile-to-backend event replay after offline queueing
- backend acceptance of the full mobile payload shape against the deployed backend base URL
- premium UI changes after real entitlement refresh
- paywall disclosure copy rendered in the final iPhone build
- closed-beta device QA script completed against the final backend host and beta build

## Still manual

- set `EXPO_PUBLIC_API_URL` to the actual live backend host
- set `EXPO_PUBLIC_ENABLE_LOGGING`
- set `VIBE_BACKEND_ENV`
- set `VIBE_BACKEND_VERSION`
- set exact `VIBE_BACKEND_ALLOWED_ORIGINS` if Expo web, browser-based testing, or web/admin surfaces are used
- set `EXPO_PUBLIC_REVENUECAT_IOS_API_KEY`
- confirm `EXPO_PUBLIC_IOS_MONTHLY_PRODUCT_ID`
- confirm `EXPO_PUBLIC_IOS_PREMIUM_ENTITLEMENT_ID`
- set real `EXPO_PUBLIC_PRIVACY_POLICY_URL`
- set real `EXPO_PUBLIC_TERMS_URL`
- confirm App Store Connect subscription group and price point
- confirm RevenueCat offering contains `vibesignal_pro_monthly_ios`
- run `python scripts/smoke_test_deployed_backend.py --base-url https://<your-backend-host>`
- run `python scripts/smoke_test_deployed_backend.py --base-url https://<your-backend-host> --include-events` if mobile event logging is in scope
- run `npm run verify:backend -- --api-url https://<your-backend-host> --event state`
- run `curl https://<your-backend-host>/healthz`
- run `curl https://<your-backend-host>/readyz`
- confirm deployed logs do not include raw chat text, request bodies, provider responses, credentials, model artifacts, vectors, or checkpoints
- record one closed-beta monitoring review using [monitoring_no_raw_logs.md](monitoring_no_raw_logs.md)
- complete [closed_beta_readiness_checklist.md](closed_beta_readiness_checklist.md) before tester invites
- complete [device_qa_script.md](device_qa_script.md) on each target beta device class
- share [closed_beta_tester_instructions.md](closed_beta_tester_instructions.md) before testers receive access

## Still missing in this workspace

- backend/admin event ingestion code
- backend/admin dashboard code
- a committed Replit deployment host or `.replit`-side deployment definition
- live server-side confirmation that the mobile event envelope fields are stored and visualized correctly
- final deployed privacy, terms, deletion, and export URLs
- legal-reviewed deletion/export support workflow and retention policy
- production monitoring and incident-response process
- alert routing and incident owner assignment
- completed release tracker entry for final closed-beta backend host, git SHA, mobile build, smoke result, log review, and device QA result

## Remaining live sandbox dependency

- an iPhone or TestFlight/dev build with sandbox App Store account access is still required before this can be called launch-ready
