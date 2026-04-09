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

## Code-complete but unverified on real device

- RevenueCat product lookup with live App Store sandbox data
- successful sandbox purchase
- restore purchases after reinstall
- mobile-to-backend event replay after offline queueing
- backend acceptance of the full mobile payload shape against the deployed backend base URL
- premium UI changes after real entitlement refresh
- paywall disclosure copy rendered in the final iPhone build

## Still manual

- set `EXPO_PUBLIC_API_URL` to the actual live backend host
- set `EXPO_PUBLIC_ENABLE_LOGGING`
- set `EXPO_PUBLIC_REVENUECAT_IOS_API_KEY`
- confirm `EXPO_PUBLIC_IOS_MONTHLY_PRODUCT_ID`
- confirm `EXPO_PUBLIC_IOS_PREMIUM_ENTITLEMENT_ID`
- set real `EXPO_PUBLIC_PRIVACY_POLICY_URL`
- set real `EXPO_PUBLIC_TERMS_URL`
- confirm App Store Connect subscription group and price point
- confirm RevenueCat offering contains `vibesignal_pro_monthly_ios`
- run `npm run verify:backend -- --api-url https://<your-backend-host> --event state`

## Still missing in this workspace

- backend/admin event ingestion code
- backend/admin dashboard code
- a committed Replit deployment host or `.replit`-side deployment definition
- live server-side confirmation that the mobile event envelope fields are stored and visualized correctly

## Remaining live sandbox dependency

- an iPhone or TestFlight/dev build with sandbox App Store account access is still required before this can be called launch-ready
