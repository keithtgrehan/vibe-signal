# iPhone Sandbox Destruction Test Plan

This plan is for the VibeSignal Expo iPhone build with the current mobile quota, premium, provider, and mobile-to-backend event logging flow. It is intentionally explicit so one test session can produce clean evidence without improvising.

## A. Pre-Test Setup

Required mobile env vars:

- `EXPO_PUBLIC_ENABLE_LOGGING=true`
- `EXPO_PUBLIC_API_URL=<reachable backend base URL>`
- `EXPO_PUBLIC_REVENUECAT_IOS_API_KEY=<RevenueCat public iOS SDK key>`
- `EXPO_PUBLIC_IOS_MONTHLY_PRODUCT_ID=vibesignal_pro_monthly_ios`
- `EXPO_PUBLIC_IOS_PREMIUM_ENTITLEMENT_ID=vibesignal_pro`
- `EXPO_PUBLIC_SUBSCRIPTION_PRICE_DISPLAY=€1.89/month`
- `EXPO_PUBLIC_PRIVACY_POLICY_URL=<real production or review-safe privacy URL>`
- `EXPO_PUBLIC_TERMS_URL=<real production or review-safe terms URL>`

Required RevenueCat assumptions:

- product `vibesignal_pro_monthly_ios` exists
- entitlement `vibesignal_pro` exists
- offering contains the monthly product
- public iOS SDK key matches the app build

Required App Store Connect assumptions:

- the monthly auto-renewing subscription exists
- the subscription is in the correct subscription group
- sandbox purchase testing is enabled for the test account
- the final App Store price point matches the displayed `€1.89/month`

Account prerequisites:

- one clean iPhone sandbox Apple account for purchase tests
- one install path with no premium history
- one reinstall path for restore tests if possible

Build prerequisites:

- current iPhone build or Expo-compatible development build installed
- backend event ingestion reachable from the device

Admin/backend observation prerequisites:

- open the server logs for `/api/events/analysis`
- open the server logs for `/api/events/quota`
- open the server logs for `/api/events/billing`
- open the server logs for `/api/events/state`
- if an admin timeline or anomaly page exists outside this repo, open it before testing

Evidence to capture:

- iPhone screenshots for every major state transition
- RevenueCat customer timeline screenshots
- App Store sandbox transaction evidence where available
- backend request logs with event IDs and statuses
- notes for any dropped, duplicated, or delayed event behavior

## B. Core Install / Bootstrap Tests

1. Delete the app from the iPhone.
2. Reinstall the current build.
3. Open the app for the first time.

Expected mobile result:

- app boots without crashing
- local analysis remains primary
- no paywall flicker during monetization bootstrap
- quota badge shows the first-week free state
- premium is inactive
- restore purchases is reachable from the paywall area when the paywall is visible later

Expected backend/admin result:

- initial state event eventually appears after bootstrap settles
- event payload includes:
  - `event_id`
  - `client_timestamp`
  - `user_id`
  - `sequence_number`
  - `session_id`
  - `platform`

Capture:

- first-open screenshot
- first state-event log line

## C. Analysis / Quota Tests

### Successful analysis

1. Tap local analysis once.

Expected mobile result:

- one successful local analysis result
- free quota decreases by exactly one

Expected backend/admin result:

- one analysis event with `success=true`
- one quota event with the matching `analysis_id`
- one state event showing the updated remaining uses

### Failed analysis

1. Trigger a local analysis failure path if available in the current test build.

Expected mobile result:

- failure is user-safe
- quota does not decrement

Expected backend/admin result:

- one analysis event with `success=false`
- no quota decrement event for that failed `analysis_id`

### Repeated rapid taps

1. Rapidly tap the local analysis button.

Expected mobile result:

- only one analysis run proceeds while one is already in progress
- no double decrement

Expected backend/admin result:

- no duplicated quota consumption for the same logical analysis

### Duplicate analysis protection

1. Re-run a captured analysis flow with the same analysis ID if the test harness allows it.

Expected mobile result:

- usage does not decrement twice

Expected backend/admin result:

- at most one quota consumption event for the same recorded analysis ID

### Quota exhaustion

1. Consume the full free quota.

Expected mobile result:

- paywall appears only after quota is exhausted
- local analysis is blocked by the paywall when premium is inactive

Expected backend/admin result:

- state events show `paywall_required=true`
- no extra quota events after exhaustion blocks further runs

## D. Purchase Tests

### Successful purchase

1. Start purchase from the paywall.
2. Complete the sandbox purchase.

Expected mobile result:

- purchase loading state is clean
- premium becomes active only after entitlement refresh confirms it
- paywall clears

Expected backend/admin result:

- purchase attempt billing event
- purchase result billing event
- entitlement refresh billing event when premium becomes active
- state event with `premium_active=true`

### Purchase cancel / failure

1. Start purchase and cancel it, or force a known failure path.

Expected mobile result:

- calm failure or cancel message
- no false premium unlock

Expected backend/admin result:

- purchase attempt billing event
- purchase result billing event showing cancellation or failure
- no premium-active state event from the failed purchase

### Purchase while catalog unavailable

1. Run a build with missing or invalid RevenueCat/App Store catalog config.

Expected mobile result:

- paywall remains honest
- purchase button is disabled or safely blocked
- fallback price display does not imply a live purchasable subscription

Expected backend/admin result:

- no false purchase success events

## E. Restore Tests

### Restore on same install

1. With an active sandbox subscription, tap restore purchases.

Expected mobile result:

- restore loading state
- premium remains or becomes active after entitlement refresh

Expected backend/admin result:

- restore attempt billing event
- restore result billing event
- entitlement refresh billing event if state changes

### Restore after reinstall

1. Delete and reinstall the app.
2. Use the same sandbox account.
3. Tap restore purchases.

Expected mobile result:

- premium returns after restore and entitlement refresh
- paywall clears only after confirmed entitlement

Expected backend/admin result:

- restore events present again for the new install session

### Restore when already active

1. Tap restore while premium is already active.

Expected mobile result:

- no crash
- active premium remains active

Expected backend/admin result:

- restore attempt and restore result are still sane
- no false downgrade

### Restore failure

1. Force an offline or config-missing restore path.

Expected mobile result:

- safe failure message
- no loss of valid cached premium if it is still within cache grace rules

Expected backend/admin result:

- restore attempt event
- restore failure event

## F. Offline / Network Chaos Tests

### Airplane mode before analysis

1. Enable airplane mode before local analysis.

Expected mobile result:

- local analysis behavior stays bounded by current app logic
- telemetry does not crash the app

Expected backend/admin result:

- events queue locally
- nothing arrives until reconnect

### Airplane mode before purchase

1. Enable airplane mode before purchase attempt.

Expected mobile result:

- purchase fails safely
- no false premium unlock

Expected backend/admin result:

- billing attempt may queue locally if emitted before failure
- no premium-active event

### Airplane mode before restore

1. Enable airplane mode before restore.

Expected mobile result:

- restore fails safely

Expected backend/admin result:

- restore attempt may queue locally
- no false entitlement activation

### Reconnect behavior

1. Re-enable connectivity.
2. Foreground the app.

Expected mobile result:

- app remains responsive

Expected backend/admin result:

- queued events replay
- ordering should follow local `sequence_number`
- duplicates should not multiply after replay

## G. App Lifecycle Chaos Tests

### Background / foreground during queued telemetry

1. Trigger local events.
2. Background the app before send.
3. Return to foreground.

Expected result:

- foreground triggers another flush attempt
- no crash and no unbounded queue growth

### Kill and reopen after enqueue but before send

1. Trigger events while offline.
2. Force-close the app.
3. Reopen later with connectivity.

Expected result:

- queued events persist across restart
- sequence numbers continue monotonically for the local install

### Reopen after long offline period

1. Leave the app offline long enough for some queued events to expire.
2. Reopen with connectivity.

Expected result:

- expired events are dropped intentionally
- drops are visible in local diagnostics
- fresher queued events still replay

## H. Sandbox Subscription Cycle Observation

1. Observe renewal or expiration behavior in sandbox timing if feasible.

Verify:

- entitlement refresh changes state correctly
- premium UI follows the entitlement rather than purchase event optimism
- backend/admin timeline shows state transitions with clear timestamps

Capture:

- RevenueCat customer timeline
- device screenshots before and after renewal or expiration
- backend state-event evidence

## I. Pass / Fail Criteria

For every major test:

- expected mobile result must match the described behavior
- expected backend/admin result must appear with sane payload shape
- any false premium unlock, false quota decrement, duplicate quota event, or repeated crashing telemetry behavior counts as a fail
- every failure should be recorded with:
  - device screenshot
  - backend log excerpt
  - event ID or analysis ID if available
  - timestamp

## J. Final Test Session Checklist

- [ ] Env vars configured
- [ ] RevenueCat product and entitlement confirmed
- [ ] App Store Connect sandbox product confirmed
- [ ] Backend event endpoints reachable
- [ ] First install boot captured
- [ ] Successful analysis captured
- [ ] Failed analysis captured
- [ ] Rapid-tap analysis protection captured
- [ ] Quota exhaustion captured
- [ ] Successful purchase captured
- [ ] Purchase cancel or failure captured
- [ ] Catalog-unavailable purchase guard captured
- [ ] Restore on same install captured
- [ ] Restore after reinstall captured
- [ ] Offline analysis behavior captured
- [ ] Offline purchase behavior captured
- [ ] Offline restore behavior captured
- [ ] Foreground flush / replay behavior captured
- [ ] Renewal or expiration observation captured if feasible
- [ ] All screenshots and logs saved
