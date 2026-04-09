# Privacy Data Flow

## Local Mode

- Mode: `local_only`
- Data stays on device:
  - raw input files
  - normalized messages and segments
  - deterministic feature outputs
  - UI payloads and optional local summary artifacts
- No external provider calls are made in this mode.

## Entitlement And Subscription State

- The sellable app path now introduces a device-scoped anonymous `app_user_id`
- Usage metering is authoritative in the local Python commerce layer, not only in mobile UI state
- Stored commerce data is limited to:
  - anonymous app-user identity
  - completed-analysis usage events
  - purchase state metadata
  - hashed purchase token or receipt references
- Raw provider API keys remain separate from commerce data and are not stored in this SQLite state path
- Raw purchase tokens or receipts should not be written to persistent plaintext storage; the current Python storage model keeps only hashed token references
- Current default development storage path is a local repo state database under `app/state/`
- This is a local development authority path, not a production multi-device account system yet

## Optional External Provider Mode

- Mode: `external_summary_optional`
- Local deterministic analysis runs first.
- Only after explicit opt-in can the app send:
  - structured signals only, or
  - structured signals plus selected excerpt text
- The local deterministic outputs remain separate from any external provider summary.
- In mobile BYOK flows, the provider credential is stored in secure on-device storage through `expo-secure-store`.
- If secure storage is unavailable, credential saving is blocked and the provider cannot move into a ready state.
- The app can now perform a lightweight live validation request before allowing the external summary flow to continue.
- Validation uses the stored provider credential and a tiny bounded request rather than a full analysis job.

## Provider-Disabled Fallback

- Mode: `provider_disabled`
- Used when a provider is not configured, not enabled, or not available.
- Local results still complete.
- Provider fallback metadata is recorded separately.

## Provider Payload Scope

- Structured signals may include:
  - shift score and comparison summaries
  - consistency level and top reasons
  - confidence/clarity trend
  - what-changed summaries
- Optional excerpt text is limited to selected excerpts only.
- Raw full conversation exports are not automatically sent to providers by default.
- Validation requests are deliberately smaller than external-summary requests and do not send the full signal bundle.
- Raw provider error bodies should not be surfaced directly to end users because providers may echo credential-shaped strings in error text.
- The app should use normalized status messages instead.

## Store Disclosure Implications

- App Store and Play Store disclosures should distinguish:
  - on-device analysis
  - optional external processing
  - provider-specific data flow when enabled
- They should also distinguish:
  - free entitlement usage counting
  - auto-renewing subscription entitlement after the free limit
  - purchase verification state and restore/sync behavior
- They should also distinguish:
  - secure on-device credential storage for optional BYOK setup
  - explicit disconnect and credential deletion support
- External providers should remain opt-in only.
