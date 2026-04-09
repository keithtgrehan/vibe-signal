# Provider Disclosure Notes

## OpenAI

- Local analysis stays on device by default.
- If OpenAI is enabled, selected structured signals and optional excerpt text may be sent to OpenAI.
- OpenAI BYOK credentials are stored securely on-device when supported.
- OpenAI can be disconnected later and its stored credential deleted.
- The app can perform a lightweight validation request before allowing the external summary flow.
- Use only content you have the right to submit.

## Anthropic

- Local analysis stays on device by default.
- If Anthropic is enabled, selected structured signals and optional excerpt text may be sent to Anthropic.
- Anthropic BYOK credentials are stored securely on-device when supported.
- Anthropic can be disconnected later and its stored credential deleted.
- The app can perform a lightweight validation request before allowing the external summary flow.
- Use only content you have the right to submit.

## Groq

- Local analysis stays on device by default.
- If Groq is enabled, selected structured signals and optional excerpt text may be sent to Groq.
- Groq BYOK credentials are stored securely on-device when supported.
- Groq can be disconnected later and its stored credential deleted.
- The app can perform a lightweight validation request before allowing the external summary flow.
- Use only content you have the right to submit.

## Product Positioning Notes

- External provider summaries must remain clearly labeled as external.
- They must not replace the deterministic-first local results.
- They must remain descriptive-only and pass the same safety validation before display.
- The UI should only show a provider as ready when secure storage is available and a BYOK credential is actually present, or when a backend proxy path is explicitly configured.
- Validation and run errors should be surfaced with short explicit statuses such as invalid credentials, timeout, rate limit, or secure storage unavailable.
- Raw provider error text should not be shown directly when it contains provider-generated credential-shaped echoes; the app should surface the normalized user-facing message instead.

## Subscription Notes

- The planned sellable app path uses store-managed billing only:
  - Apple StoreKit on iOS
  - Google Play Billing on Android
- Current pricing scaffold:
  - `10` free completed analyses total per anonymous app user
  - then `€1.89/month` auto-renewing
- BYOK provider charges remain separate from the app subscription.
- The app subscription unlocks VibeSignal AI usage after the free limit.
- It does not replace or hide any costs a user may separately incur with OpenAI, Anthropic, or Groq under BYOK.
- The repo does not claim App Store or Play compliance yet; it only prepares the billing architecture and entitlement logic for that wiring.
