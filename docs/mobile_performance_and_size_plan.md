# Mobile Performance And Size Plan

This is a practical launch-stage performance and size note for the current Expo mobile shell. It is not a full profiling report.

## Optimized In Code Now

- primary local analysis flow is back at the top of the mobile screen
- external AI setup is collapsed by default so the first screen is lighter
- provider verification happens only when the user explicitly asks for it
- local analysis stays deterministic and does not depend on provider setup
- lightweight recent-analysis history is capped at `3` items
- local analysis output stays structured and short enough for screenshot/share use
- paywall state remains bounded and non-blocking during bootstrap
- event logging stays fire-and-forget and queue-based

## Current Likely Size Contributors

- Expo runtime
- React Native core
- `react-native-purchases`
- `expo-secure-store`
- `expo-document-picker`
- `expo-file-system`

The recent additions for upload support are intentional and scoped:

- `expo-document-picker`
- `expo-file-system`
- `expo-clipboard`

No additional heavy analytics or monitoring SDK was added in this pass.

## What Still Needs Device Measurement

- first-screen render feel on iPhone
- keyboard interaction with the multiline input
- upload latency for a typical text file
- paywall render height on smaller phones
- app startup responsiveness in Expo/dev build and in the final iOS build
- App Store archive size once the release build exists

## Practical “Good Enough For Apple” Targets

- no hidden primary input on first open
- no horizontal overflow on iPhone-sized screens
- no keyboard overlap blocking the main input
- no dead purchase or restore buttons
- no misleading purchasable state when product metadata is unavailable
- no provider setup requirement before local analysis
- no obvious crash path when secure storage, logging, or billing config is incomplete

## What To Watch During Sandbox Testing

- first paint and scroll smoothness on the root screen
- keyboard resize behavior around the multiline input
- file upload path on-device
- paywall visibility only after real quota exhaustion
- purchase and restore loading states staying responsive
- no repeated or delayed UI churn after entitlement refresh
