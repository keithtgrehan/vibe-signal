# VibeSignal AI Mobile Support

This folder contains the mobile-ready BYOK layer for optional provider connectors plus the current iOS-first subscription and quota scaffolding.

The app will **not** connect to a backend unless `EXPO_PUBLIC_API_URL` is provided.

## Current Mobile UX Guarantees

The current Expo shell now keeps the local analysis path obvious on small screens:

- one mobile-first column
- bounded content width
- the primary text input is always visible
- upload and analyze actions stay in the primary card
- keyboard-safe layout on iPhone-sized screens
- the external provider section stays optional and collapsed by default
- provider setup never blocks local analysis
- recent analysis results can be reopened locally

The current BYOK flow guarantees:

- no provider selected
- provider selected
- key entered
- verifying
- verified
- failed

Behavioral guarantees:

- `Verify key` only enables when the entered key length is greater than `10`
- invalid keys are not saved
- successful verification saves the key and returns `Key verified and saved`
- secure storage remains primary on iOS
- web falls back to localStorage only when a real round-trip probe succeeds
- remove-key flow is available once a credential exists

The current local analysis result flow also guarantees:

- deterministic local signal extraction
- structured output with:
  - pattern
  - what changed
  - where
- guardrail cleanup before render
- share/copy actions from the result card
- recent local history limited to the last `3` analyses

## Mobile Backend Event Logging

The Expo mobile shell now includes a bounded mobile-to-backend event pipeline for the existing VibeSignal event endpoints.

Required env vars:

- `EXPO_PUBLIC_ENABLE_LOGGING`
  - enables outbound mobile event logging when set to a truthy value such as `1`, `true`, `yes`, or `on`
- `EXPO_PUBLIC_API_URL`
  - base backend URL used for:
    - `POST /api/events/analysis`
    - `POST /api/events/quota`
    - `POST /api/events/billing`
    - `POST /api/events/state`

Shared payload fields now sent on every event:

- `event_id`
- `client_timestamp`
- `user_id`
- `sequence_number`
- `session_id`
- `platform`
- `app_version`

Event-specific fields:

- analysis event
  - `analysis_id`
  - `success`
  - `mode`
  - `status`
- quota event
  - `type`
  - `remaining_after`
  - `analysis_id`
- billing event
  - `type`
  - `status`
  - `product_id`
  - `entitlement_name`
- state event
  - `premium_active`
  - `remaining_uses`
  - `paywall_required`
  - `current_period_type`
  - `purchase_in_progress`
  - `restore_in_progress`

Queue, retry, and dedupe behavior:

- queue is stored locally through `expo-secure-store`
- queue length is bounded
- seen event IDs are bounded
- sequence numbers persist across normal app restarts through the queue state
- repeated event IDs are deduped before resend
- failed sends retry up to the configured max-attempt limit
- expired events are dropped intentionally instead of persisting forever
- logging is fire-and-forget and does not throw into the UI flow
- local debug state includes queue length, drop counters, dedupe count, and scheduled retry count

State snapshot behavior:

- state snapshots are diff-aware first
- unchanged tracked state is not resent
- tracked fields are debounced before send
- state logging is emitted from the shared quota/monetization layer, not from raw render loops

Flush behavior:

- queued events flush on startup
- queued events flush shortly after enqueue
- queued events flush on app foreground
- queued events schedule a bounded retry after retryable send failures

Current guarantees:

- callers do not await telemetry for purchase, restore, analysis, or state updates
- logging becomes a safe no-op when env config is missing or disabled
- local quota and billing behavior do not depend on telemetry success

Current limits:

- reconnect-triggered flush is not implemented because this checkout does not yet include a dedicated network-status listener
- event ordering is strongest within one device and one local install because ordering depends on device-local persisted sequence numbers
- `app_version` is included in the envelope shape, but this shell leaves it empty unless `EXPO_PUBLIC_APP_VERSION` is configured
- the backend/admin event-ingestion code is not present in this workspace, so backend compatibility is enforced from the mobile contract side only

## Replit / Backend Wiring

This repo is not hard-wired to a committed Replit deployment host.

What is wired in code:

- the mobile event client is environment-driven through `EXPO_PUBLIC_API_URL`
- event endpoints are appended from that base URL:
  - `/api/events/analysis`
  - `/api/events/quota`
  - `/api/events/billing`
  - `/api/events/state`

What is not committed in this repo:

- a `.replit` file
- a `replit.nix` file
- a hardcoded `replit.app` backend host

Current verification result from this environment:

- the provided public workspace URL `https://replit.com/@grehanke/Vibe-Signal` returned `404`
- because of that, the repo cannot safely infer the live deployment host from source control alone

Required next step:

- set `EXPO_PUBLIC_API_URL` explicitly to the live deployed backend base URL used by the Replit deployment

One-shot backend acceptance check:

- `npm run verify:backend -- --api-url https://<your-backend-host> --event state`

Full endpoint sweep:

- `npm run verify:backend -- --api-url https://<your-backend-host> --all`

This sends one minimal valid event payload and prints the response status/body so the deployed backend can be checked without repeatedly spamming the event routes.

## Monetization Status

- Apple billing path chosen:
  - `react-native-purchases` (RevenueCat React Native SDK) for the iOS premium unlock path
- Premium unlocking path:
  - Apple App Store subscription entitlement on iOS
  - no custom checkout
  - no Stripe or web payment bypass
- Current monthly premium display price:
  - `€1.89/month`
- Runtime monetization config expected by this shell:
  - `EXPO_PUBLIC_REVENUECAT_IOS_API_KEY`
  - `EXPO_PUBLIC_IOS_MONTHLY_PRODUCT_ID`
  - `EXPO_PUBLIC_IOS_PREMIUM_ENTITLEMENT_ID`
  - `EXPO_PUBLIC_SUBSCRIPTION_PRICE_DISPLAY`
  - `EXPO_PUBLIC_PRIVACY_POLICY_URL`
  - `EXPO_PUBLIC_TERMS_URL`
- Free usage policy currently implemented in app state:
  - first 7 days: `10` free completed analyses
  - after that: `5` free completed analyses every 7-day period
- Paywall trigger:
  - when the current free period is exhausted and premium is not active
- Restore path:
  - implemented in the mobile commerce layer
- Premium caching:
  - the app keeps a short-lived cached premium state so active subscribers are not randomly locked during a temporary refresh failure
- Mobile UI integration now uses the real commerce state:
  - [useQuota.js](/Users/keith/Desktop/VibeSignal AI/mobile/src/hooks/useQuota.js) hydrates quota, premium, paywall, restore, and purchase state from the shared monetization service
  - [quotaViewModel.js](/Users/keith/Desktop/VibeSignal AI/mobile/src/hooks/quotaViewModel.js) keeps the UI-facing quota shape consistent across service and screen rendering
  - [QuotaBadge.js](/Users/keith/Desktop/VibeSignal AI/mobile/src/components/QuotaBadge.js) renders real remaining-use state
  - [PaywallCard.js](/Users/keith/Desktop/VibeSignal AI/mobile/src/components/PaywallCard.js) is wired to the actual purchase and restore actions
  - [ProviderSettingsScreen.js](/Users/keith/Desktop/VibeSignal AI/mobile/src/screens/ProviderSettingsScreen.js) now uses the live quota/premium state instead of placeholder values
- Successful local analyses now decrement free usage through the gated commerce flow only after the local analysis callback resolves successfully
- Failed or blocked analysis attempts do not decrement quota
- The billing catalog path now forwards the device app-user ID into product lookup, which matches how RevenueCat-backed product discovery will be exercised on device
- Unavailable secure storage now returns a consistent monetization shape for the UI instead of leaving the shell to infer missing fields
- Premium truth now comes from the named RevenueCat entitlement:
  - `vibesignal_pro`
- Purchase and restore actions are now single-flight guarded so overlapping billing actions do not race each other
- Initial app hydration now exposes an explicit bootstrapping state so the shell does not flash a paywall before entitlement and catalog sync complete
- Persisted completed-analysis IDs now support longer idempotency history across app restarts
- Fallback catalog metadata can still show display pricing, but premium purchase is blocked until a live valid StoreKit/RevenueCat product is available
- Paywall and subscription surfaces now include:
  - restore purchases action
  - monthly billing disclosure
  - auto-renewal disclosure
  - cancellation reminder via Apple account settings
  - config-driven Privacy Policy and Terms link support using secure `https://` URLs only
  - honest disabled purchase state when the live product is not available

Important limits:

- Real Apple purchase execution still needs:
  - an iOS development build or TestFlight/App Store build
  - RevenueCat iOS public SDK key configuration
  - App Store Connect product and entitlement setup
- The exact live monthly price must match the App Store Connect subscription price point
- This repo now contains the iOS code path, quota engine, and paywall state logic, but it does not claim production readiness on its own

## Sandbox Readiness Helpers

Useful commands:

- `npm test`
- `npm run verify:backend -- --api-url https://<your-backend-host> --event state`
- `npm run verify:backend -- --api-url https://<your-backend-host> --event analysis`

These helper commands do not prove App Store billing works. They only help confirm:

- mobile payload shape is valid
- the configured backend base URL is reachable
- the deployed backend accepts at least one sample event route

## Expo SDK 54 Status

- The mobile app has been upgraded incrementally from Expo SDK `52` to `53` and then to `54`
- Current mobile dependency set:
  - `expo` `^54.0.33`
  - `expo-asset` `~12.0.12`
  - `expo-secure-store` `~15.0.8`
  - `react` `19.1.0`
  - `react-native` `0.81.5`
- `npx expo-doctor` is clean on this repo
- `npm test` passes on this repo
- `npx expo config` resolves with `sdkVersion: 54.0.0`
- This project is now aligned with the current Expo Go SDK 54 line
- On this machine, the remaining execution gap is iOS simulator/device launch proof:
  - Homebrew `node`, `npm`, and `npx` are available
  - `xcrun simctl` is still unavailable here
  - Expo project initialization is now runtime-proven through the local Expo binary
  - full Metro port bind and iOS launch proof are still not captured here
- The stale Expo Router ambiguity has been narrowed:
  - the old `Using src/app as the root directory for Expo Router.` message was caused by a leftover empty `mobile/src/app/` directory
  - that directory has been removed
  - normal startup no longer prints that `src/app` router message
  - with `EXPO_DEBUG=1`, Expo still prints a debug-only fallback line about `app` from its internal router helper

Validation commands used for the upgrade pass:

- `PATH=/opt/homebrew/bin:$PATH npm install`
- `PATH=/opt/homebrew/bin:$PATH npx expo install --fix`
- `PATH=/opt/homebrew/bin:$PATH npx expo-doctor`
- `PATH=/opt/homebrew/bin:$PATH npm test`
- `PATH=/opt/homebrew/bin:$PATH npx expo config`
- `PATH=/opt/homebrew/bin:$PATH ./node_modules/.bin/expo start --clear`
- `PATH=/opt/homebrew/bin:$PATH ./node_modules/.bin/expo export --help`

- Secure secret storage uses `expo-secure-store`
- iOS storage maps to Keychain-backed secure storage through Expo
- Android storage maps to encrypted native secure storage through Expo
- The Expo app config now includes the `expo-secure-store` plugin in [app.json](/Users/keith/Desktop/VibeSignal AI/mobile/app.json)
- No provider secret is written to plaintext files, AsyncStorage, localStorage, or SQLite
- If secure storage is unavailable, credential writes fail closed
- Device-scoped anonymous identity is also stored through secure storage for the sellable app path
- A minimal Expo-style screen now exists in [App.js](/Users/keith/Desktop/VibeSignal AI/mobile/App.js), [index.js](/Users/keith/Desktop/VibeSignal AI/mobile/index.js), and [ProviderSettingsScreen.js](/Users/keith/Desktop/VibeSignal AI/mobile/src/screens/ProviderSettingsScreen.js)
- The current mobile flow supports:
  - provider selection
  - API key entry
  - secure save / update
  - secure removal
  - consent acknowledgement
  - readiness display
  - lightweight live validation
  - gated external-summary request flow

What is implemented:

- provider catalog and provider-specific lightweight validation requests
- masked saved-key display helpers
- billing catalog and configurable product metadata for:
  - `vibesignal_pro_monthly_ios`
  - `vibesignal_pro_monthly_android`
- iOS-first premium path via RevenueCat's React Native SDK on top of the App Store billing system
- local quota engine for:
  - first-week `10` free completed analyses
  - later `5` free completed analyses per 7-day period
- paywall state helpers and selectors for:
  - uses left
  - period label
  - reset timing
  - premium active
  - paywall visibility
- restore purchases and entitlement refresh surfaces for iOS
- device identity helpers for a device-scoped anonymous app user path
- explicit fail-closed installation-identity handling:
  - no AsyncStorage fallback
  - no localStorage fallback
  - no plaintext file fallback
- iOS-first billing adapter surfaces for:
  - readiness inspection
  - initialization
  - product lookup
  - purchase attempt normalization
  - restore artifact normalization
- entitlement client contracts for:
  - fetch entitlement
  - submit purchase verification
  - restore purchases
  - record completed analysis
- thin StoreKit and Google Play Billing adapter interfaces
- normalized purchase-attempt and restore result shapes that stay unverified until the Python commerce layer confirms entitlement
- validation result mapping for:
  - `ready`
  - `missing_credentials`
  - `secure_storage_unavailable`
  - `invalid_credentials`
  - `provider_timeout`
  - `rate_limited`
  - `provider_unavailable`
  - `consent_required`
  - `unknown_error`
- run gating so the external summary path does not proceed when consent, storage, key, or validation state is invalid
- on-device monetization state now exists for the Expo mobile shell while the older Python commerce scaffolding remains in the repo for the broader project

What still depends on later store wiring:

- RevenueCat public iOS SDK key configuration
- App Store Connect setup for:
  - subscription product `vibesignal_pro_monthly_ios`
  - subscription group
  - final price point confirmation
- iOS development build / TestFlight validation for real purchases and restores
- real Google Play Billing purchase initiation
- real App Store / Play receipt or purchase-token verification
- restore/sync execution against live store accounts
- mobile UI for purchase, restore, and paywall presentation
  - the current Expo shell now has the real wiring for quota and paywall state, but still needs on-device iPhone sandbox validation for the Apple purchase path
- backend/admin event-ingestion implementation
  - this mobile repo now sends the bounded event contract, but the actual server-side ingestion code is not present here

Still unverified here:

- no real provider keys were exercised in this environment
- the Expo UI was not launched on iPhone or simulator from this machine
- `xcrun simctl` is not available on this machine
- `./node_modules/.bin/expo start --clear` reaches project startup on this machine, but I did not capture a stable Metro port bind
- a debug-only Expo router fallback line still appears when `EXPO_DEBUG=1`, even though normal startup no longer prints the old `src/app` router message
- the iOS billing adapter is now structurally more concrete, but no real StoreKit bridge package could be installed or executed here
- no real purchase flow was executed in this environment

Local JavaScript tests live under [mobile/tests](/Users/keith/Desktop/VibeSignal AI/mobile/tests) and they now run successfully with the Homebrew Node toolchain on this machine.
- Current test count:
  - `81` passing tests

Proof artifacts from the current validation pass live under:

- [docs/proof/phase_validation_2026-04-07](/Users/keith/Desktop/VibeSignal AI/docs/proof/phase_validation_2026-04-07)
