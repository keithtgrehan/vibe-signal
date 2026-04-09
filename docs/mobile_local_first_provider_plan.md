# Mobile Local-First Provider Plan

## Core Direction

- Local deterministic analysis remains the default product path.
- External AI providers remain optional and off by default.
- Mobile clients must never ship provider-owned backend keys.
- Mobile BYOK credentials must be stored securely on-device or not stored at all.

## Authentication Models

- `byok`
  - user supplies their own provider credential
  - implemented mobile storage path:
    - `expo-secure-store` in [mobile/src/secureStorage/providerSecureStore.js](/Users/keith/Desktop/VibeSignal AI/mobile/src/secureStorage/providerSecureStore.js)
    - iOS maps to Keychain-backed secure storage through Expo
    - Android maps to encrypted native secure storage through Expo
- `backend_proxy`
  - provider calls are routed through an app-owned backend
  - the mobile app must not contain the backend provider secret
- `disabled`
  - no provider calls are allowed

## Secure Storage Expectations

- BYOK credentials are not stored in plaintext preferences or source code.
- The implemented mobile service exposes:
  - `saveProviderCredential`
  - `getProviderCredential`
  - `deleteProviderCredential`
  - `clearAllProviderCredentials`
  - `secureStorageAvailable`
- If secure storage is unavailable, credential saving fails closed with `credential_save_blocked`.
- Disconnecting a provider deletes its stored credential.
- Provider configuration stays separate from local deterministic artifacts.

## Consent Expectations

- Local analysis should stay on device by default.
- External AI should require clear, provider-specific consent.
- The app should disclose:
  - which provider is selected
  - whether structured signals only or signals plus excerpt text will be sent
  - that the provider can be disconnected later

## Current Scope

- This repo now includes:
  - provider flags and provider config interfaces
  - provider consent payloads
  - provider adapter scaffolding
  - secure mobile credential storage in [mobile/](/Users/keith/Desktop/VibeSignal AI/mobile)
  - frontend-safe provider readiness payloads with secure-storage-aware states
  - a minimal Expo-style provider settings screen and controller flow
  - lightweight live validation request builders for OpenAI, Anthropic, and Groq
  - gated external-summary request flow using the stored BYOK credential
- It still does not include:
  - backend proxy infrastructure
  - live provider verification with real credentials in this environment
  - an app-store-polished mobile UX pass
