# VibeSignal

VibeSignal is a deterministic-first conversation analysis product with a mobile shell, optional BYOK AI augmentation, and privacy-conscious boundaries.

The repo is strongest as a productized workflow demo: local analysis runs first, outputs stay structured and inspectable, and any external provider layer is explicitly optional rather than presented as hidden truth.

## What It Is
- A mobile-first app for spotting conversation pattern shifts in pasted messages or short exchanges.
- A deterministic local signal engine that highlights what changed, where it changed, and which patterns triggered the result.
- An optional BYOK provider layer for structured augmentation after explicit opt-in.
- A bounded product shell around that core flow: recent history, copy/share behavior, premium gating scaffolding, and backend event contracts.

## Why It Exists
Many message-analysis products overclaim. VibeSignal takes the narrower path:
- pattern detection, not certainty
- structured outputs, not raw-text magic
- local-first analysis, with optional external AI only when configured
- descriptive language, not accusations or diagnoses

This makes it easier to discuss the product with recruiters, interviewers, or operators as a workflow and trust-boundary exercise instead of an "AI knows what they meant" pitch.

## What The Product Outputs
Current deterministic outputs center on conversation-pattern shifts such as:
- tone
- directness
- vagueness
- hedging
- urgency
- response alignment

The product surfaces those as structured "what changed" results rather than as hidden scores alone.

## Current Repo Reality
Built now:
- Expo mobile shell with an always-available local analysis path
- deterministic local analysis and structured result rendering
- recent-analysis persistence plus copy/share actions
- optional BYOK provider validation and secure on-device storage when supported
- bounded mobile-to-backend event logging with retry, validation, and diagnostics
- quota, paywall, and RevenueCat-oriented mobile scaffolding
- privacy, provider-disclosure, and prelaunch-readiness documentation

Code-complete but still needing real-world proof:
- deployed backend verification against the final live host
- iPhone simulator/device runtime proof
- RevenueCat/App Store sandbox purchase and restore validation
- final production privacy / terms URLs

## Architecture Snapshot
- `mobile/`: Expo / React Native shell, provider setup, quota state, billing scaffolding, and event logging
- `src/vibesignal_ai/`: deterministic conversation analysis, contracts, providers, safety rules, and UI payload builders
- `docs/`: privacy flow, provider disclosure, backend contract notes, and execution-proof material
- `docs/proof/phase_validation_2026-04-07/`: bounded validation artifacts for the current mobile/provider pass

The important repo boundary is simple: deterministic local artifacts are the source of truth, and optional provider outputs are late-bound add-ons.

## Privacy And AI Boundary
- Local deterministic analysis is the default path.
- External AI is optional and BYOK-driven.
- Provider configuration stays separate from deterministic artifacts.
- Secure on-device credential storage is preferred when supported.
- The repo does not claim deception detection, intent inference, diagnosis, or mental-health judgment.

## How To Review The Repo
Start here if you want the fastest credible walkthrough:
- [mobile/README.md](mobile/README.md) for the current mobile shell, BYOK, event logging, and monetization state
- [docs/privacy_data_flow.md](docs/privacy_data_flow.md) for privacy and data-handling boundaries
- [docs/provider_disclosure_notes.md](docs/provider_disclosure_notes.md) for optional provider positioning
- [docs/legal_safe_output_policy.md](docs/legal_safe_output_policy.md) for wording and safety constraints
- [docs/proof/phase_validation_2026-04-07/final_phase_validation_summary.md](docs/proof/phase_validation_2026-04-07/final_phase_validation_summary.md) for bounded execution proof

## Running The Current Repo
Python package setup:

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest
```

Mobile shell:

```bash
cd mobile
npm install
npm test
npm start
```

Optional backend contract check:

```bash
cd mobile
npm run verify:backend -- --api-url https://<your-backend-host> --event state
```

## Recruiter / Interview Framing
This repo is best presented as:
- a deterministic-first conversation-analysis product
- a mobile wrapper around structured local signals
- an example of optional AI augmentation with clear boundaries
- a privacy-aware workflow with explicit BYOK and telemetry constraints

It should not be presented as:
- a lie detector
- a hidden-intent engine
- a diagnostic system
- a fully production-proven subscription app

## Repo Truthfulness
Keep the story narrow:
- built now
- code-complete but not yet fully validated in live mobile/backend conditions
- future work only where explicitly labeled

No fake certainty. No unsupported claims.
