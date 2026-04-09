# VibeSignal

VibeSignal is a mobile-first AI product for reading conversational pattern shifts more clearly and safely.

## What it does

Paste a message or short conversation and VibeSignal highlights what changed in:

- tone
- directness
- vagueness
- hedging
- urgency
- response alignment

It is designed as a second perspective, not a source of truth.

## Product aim

The goal is to help users quickly spot changes in how something reads, especially when a reply feels different, less clear, more indirect, or subtly off.

Core product principle:

- pattern detection, not certainty
- evidence-backed output, not hidden truth claims
- local-first analysis with optional external AI

## Current product state

### Built now

- mobile-first primary analysis flow
- always-visible local input path
- deterministic local signal engine
- structured result output:
  - pattern
  - what changed
  - where
- recent-analysis persistence
- copy/share support
- optional BYOK provider flow
- verify-before-save provider validation
- event logging pipeline with retry, validation, and diagnostics
- backend verification helper tooling
- paywall / monetization readiness groundwork
- sandbox and prelaunch readiness docs

### Code-complete but still needs real-world validation

- real deployed backend verification
- real iPhone Safari / WKWebView feel check
- RevenueCat / App Store sandbox purchase flow
- restore flow on device
- entitlement refresh validation
- telemetry replay against live backend

## Tools and stack

### Mobile / product
- Expo
- React Native
- JavaScript
- secure storage on iOS
- localStorage fallback for web where appropriate

### Product systems
- deterministic local signal analysis
- bounded local analysis history
- event queue with retry / validation / diagnostics
- backend verification tooling

### Monetization / compliance groundwork
- RevenueCat-oriented readiness checks
- restore purchases path
- privacy / terms link handling
- App Store prelaunch documentation

## Analytical basis

VibeSignal currently uses a lightweight deterministic analysis layer rather than a large local ML stack.

It looks for practical language-pattern shifts such as:

- increased hedging
- increased vagueness
- lower lexical overlap / weaker response alignment
- tone or urgency changes
- meaningful message-length shifts

This is not a diagnostic system, not a lie detector, and not a mental health tool.

## Legal and ethical positioning

VibeSignal is intended as a decision-support and interpretation-support product.

It does **not** claim to:

- detect deception
- infer hidden intent with certainty
- diagnose mental health
- replace professional advice
- provide legal, medical, or psychological judgments

The product should remain:

- evidence-first
- low-hype
- safe in wording
- non-accusatory
- grounded in visible text

## How outcomes will be measured

Success should be measured with real product metrics, not vague engagement claims.

### Activation
- first successful analysis rate
- time to first result
- example-to-analysis conversion

### Retention
- D1 return rate
- D7 return rate
- repeat analyses per user
- recent-analysis reopen usage

### Monetization
- free-to-premium conversion
- upgrade after quota exhaustion
- restore success rate
- purchase success rate

### Product quality
- output usefulness feedback
- share/copy usage
- crash/error rates
- backend event acceptance rate
- sandbox test pass rate

## Monetisation goals

Near-term monetisation goal:

- make the local product useful first
- prove premium adds deeper value
- validate subscription flow safely before scaling

Premium should feel like:
- deeper analysis
- more detail
- optional external AI augmentation
- not basic access to the product’s core usefulness

## Adoption goals

Early adoption should focus on:

- users who already overthink tone in messages
- users comparing replies
- users wanting a second interpretation quickly
- creators/demo audiences who can show clear before/after examples

Healthy early signs:
- repeat usage
- screenshots/shares
- high first-result completion
- users voluntarily trying multiple messages

## Shareability / “going viral”

Virality is not assumed. It has to be earned.

The realistic loop is:

- fast first-use curiosity
- surprisingly useful output
- screenshot-friendly result
- easy share/copy behavior
- strong “try this on another message” loop

What matters most:
- product clarity
- result quality
- emotional relevance
- low friction

## Long-term vision

Longer term, VibeSignal could evolve into a broader language-pattern platform with:

- stronger local signal analysis
- optional structured LLM augmentation with guardrails
- better observability and operator tooling
- cleaner trust/safety controls
- better premium differentiation
- reusable pattern-analysis infrastructure for future tools

## What is still left to do

- confirm live backend wiring with the real deployed URL
- set final EXPO_PUBLIC_API_URL
- run full backend verification against production-like endpoints
- complete real iPhone sandbox destruction test run
- finalize RevenueCat / App Store Connect setup
- add final production Privacy Policy URL
- add final production Terms URL
- confirm real purchase / restore behavior on device

## Running the project

See the repo and mobile/README.md for current setup and verification steps.

## Repo truthfulness

This repo should distinguish clearly between:

- built now
- code-complete but unverified on device
- planned / future work

No fake certainty. No unsupported claims.
