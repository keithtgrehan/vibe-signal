# VibeSignal

VibeSignal is a local-first conversation pattern analysis product with an Expo mobile app path, an optional BYOK external-summary layer, and an iOS-first subscription/quota system prepared for App Store billing.

It is built for people who want help noticing communication shifts, consistency changes, tone movement, and comparison patterns across conversations without turning that into a verdict engine. The current product is designed to support interpretation, not to declare truth.

## What VibeSignal Is

VibeSignal helps a user inspect how a conversation changes over time.

Today, the repo supports:

- deterministic-first analysis for chats and transcript-like inputs
- safe UI payload generation for product surfaces
- optional BYOK provider summaries that remain secondary to local results
- secure on-device credential storage in the mobile layer
- iOS-first monetization, quota, and paywall scaffolding
- mobile-to-backend event logging for quota, billing, analysis, and state telemetry

The core user problem is simple: people often feel that a conversation is shifting, but they struggle to describe what changed. VibeSignal aims to turn that into a structured, reviewable pattern summary.

## Product Aim

The near-term product goal is to ship a trustworthy mobile app that:

- keeps local pattern analysis primary
- adds optional premium access through App Store billing
- makes external AI summaries optional, labeled, and subordinate
- gives the team enough telemetry and diagnostics to operate the product safely

The user outcome is clarity. Not certainty, not accusation, and not prediction. The product matters if it helps a user compare earlier versus later behavior, spot changes in specificity or pacing, and reflect with more structure than intuition alone.

## Tools And Stack

This repo currently uses the following real stack:

- Python analysis pipeline under [`src/vibesignal_ai`](/Users/keith/Desktop/VibeSignal AI/src/vibesignal_ai)
- Expo / React Native mobile shell under [`mobile/`](/Users/keith/Desktop/VibeSignal AI/mobile)
- `expo-secure-store` for provider credentials and installation identity
- `react-native-purchases` as the iOS-first RevenueCat / StoreKit subscription path
- bounded mobile event queueing, validation, retry, and diagnostics in the Expo app
- SQLite-backed local commerce authority in the Python side for development and contract work
- deterministic feature modules for directness, specificity, consistency, confidence/clarity, and “what changed” style outputs

Supporting libraries already declared in the repo include:

- `emoji`
- `langdetect`
- `rapidfuzz`
- `pysbd`
- `spacy`

Optional heavier integrations are scaffolded but not part of the default path.

## Analytical Basis

VibeSignal is currently best understood as a deterministic and product-logic-driven analysis system, not as a fully trained end-to-end ML product.

The repo analyzes patterns such as:

- changes in tone and directness
- changes in specificity and detail
- shifts in consistency across turns or replies
- changes in pacing, clarity, or confidence cues
- earlier-versus-later differences in how someone responds

Psychology and behavioral framing appear here as interpretation scaffolding, not as clinical diagnosis or hidden-intent detection. The product tries to describe observable conversational patterns in a structured way.

What it does **not** claim:

- it is not a lie detector
- it does not determine cheating, honesty, intent, or guilt
- it does not read minds
- it does not prove what someone meant
- it is not a validated mental-health or forensic instrument

There is experiment scaffolding in the repo for datasets and calibration work, but the current product path is still primarily heuristic, rule-based, and product-logic-led. The README and docs intentionally do not claim proprietary training sets, model benchmarks, or validated predictive accuracy that do not exist here today.

## Legal And Ethical Positioning

VibeSignal is not:

- a mental health diagnosis tool
- a law-enforcement tool
- a lie detector
- a substitute for qualified legal, medical, therapeutic, or safeguarding advice

Current privacy handling in the repo is high-level and grounded:

- local analysis remains the default path
- optional BYOK provider summaries are opt-in only
- provider keys are stored in secure on-device storage when supported
- premium and quota state are handled separately from BYOK credentials
- mobile telemetry is bounded, validated, and queue-based
- the backend/admin ingestion code is not present in this workspace, so server-side storage and admin behavior are documented as external dependencies, not claimed as complete here

The repo is being prepared for App Store-compliant monetization, restore flows, disclosure copy, and legal-link surfaces, but it does not claim App Store approval or production billing validation yet.

## Current State

### Built now

- deterministic conversation analysis pipeline
- structured artifacts and UI payload generation
- safety validators and banned-term filtering
- optional external provider summary path for OpenAI, Anthropic, and Groq
- secure mobile BYOK credential storage and validation flow
- Expo SDK 54 mobile app shell
- iOS-first quota, paywall, entitlement, and restore scaffolding
- RevenueCat / StoreKit-compatible subscription path in code
- mobile logging pipeline with bounded queue, validation, dedupe, retry, and diagnostics
- repo-local docs for sandbox testing and prelaunch readiness
- automated tests for quota, billing, provider flows, logging, diagnostics, and summary safety

### Code-complete but still unverified on device

- live App Store sandbox purchase flow
- live restore-after-reinstall flow
- live RevenueCat product lookup with final production config
- end-to-end backend acceptance of the mobile telemetry envelope against the deployed server

### Planned / future

- stronger backend/admin observability once that code is wired in the deployment environment
- richer post-analysis product surfaces
- safer and deeper experimentation around provider-assisted summaries

## What Is Left To Do

The main remaining work is no longer broad architecture. It is operational validation and store-side setup:

- real iPhone sandbox purchase and restore validation
- final RevenueCat configuration checks
- App Store Connect subscription product and price-point confirmation
- final production Privacy Policy and Terms URLs
- App Store submission assets, metadata, screenshots, and review notes
- deployed backend/admin verification that mobile telemetry fields are accepted and rendered as expected

## How We Will Drive And Measure Outcomes

The short-term goal is not abstract “AI engagement.” It is a product that is understandable, safe, retained, and monetizable.

### Product outcomes to drive

- a user can complete a first analysis without confusion
- the free quota model is understandable and predictable
- premium upgrade is available, restorable, and not misleading
- provider configuration is optional and does not weaken the local-first default
- the team can see enough telemetry to debug onboarding, quota, and billing issues

### What success looks like

- users complete analyses successfully
- premium state remains accurate and recoverable
- paywall transitions are understandable
- restore works when it should
- crashes, duplicate usage consumption, and telemetry blind spots stay low

### Metrics that matter in the near term

- activation
  - install to first successful analysis
- successful analysis completion
  - percentage of started analyses that complete cleanly
- paywall conversion
  - quota exhaustion to premium purchase attempt
- restore success
  - restore attempt to active premium
- quota exhaustion to upgrade conversion
  - how many exhausted users try premium
- retention / repeat use
  - repeat analysis usage across periods
- crash and error rate
  - especially around purchase, restore, quota, and secure storage
- App Store review readiness
  - restore reachable, legal links present, disclosure copy truthful
- support and diagnostic signal quality
  - whether mobile telemetry and diagnostics explain failures cleanly

### What exists today to support measurement

- mobile event logging for:
  - analysis
  - quota
  - billing
  - monetization state
- internal diagnostics buffer for config, billing, and telemetry warnings
- docs for sandbox destruction testing and prelaunch checks

The repo does **not** include the backend/admin ingestion code in this workspace, so any server-side dashboards or anomaly pages remain external dependencies.

## Monetisation Goals

The immediate monetisation goal is narrow and testable:

- prove that the quota model is understandable
- prove that the App Store premium path can be configured and restored safely
- validate that users who hit quota can see, understand, and trust the upgrade path

Current monetisation design in code:

- first 7 days: 10 free completed analyses
- after that: 5 free completed analyses per 7-day period
- premium subscription target display: `€1.89/month`
- premium unlock path: Apple App Store billing via RevenueCat / StoreKit integration path

Before any broader launch or paid acquisition, the product still needs:

- real sandbox purchase validation
- real restore validation
- final App Store Connect pricing confirmation
- proof that telemetry makes quota and billing issues debuggable

## Adoption Goals

The likely earliest users are:

- people comparing shifts in their own conversations
- users curious about communication patterns rather than verdicts
- early testers comfortable with a reflective, pattern-based tool

Healthy early-product signals would look like:

- users finishing at least one analysis
- users returning to compare another conversation or another time window
- clear quota and paywall comprehension
- support questions focused on setup or interpretation rather than billing confusion or broken trust

## “Going Viral” Positioning

Virality is a growth hypothesis, not a current repo achievement.

If VibeSignal eventually earns word-of-mouth, it will likely come from:

- a result that feels specific and memorable
- repeat use across multiple conversations
- clean demoability in screenshots or short creator walkthroughs
- trustable product framing that avoids sensational claims
- App Store discoverability once submission quality is strong

What has to happen first:

- the product has to feel safe
- the quota and premium path have to feel fair
- analysis outputs have to feel useful without sounding accusatory
- restore and subscription behavior have to be boringly reliable

## Long-Term Vision

If the current launch-stage product works, the longer-term opportunity is broader than a single screen or quota flow.

Potential evolution paths that fit the current direction:

- richer conversation comparison surfaces
- stronger backend observability and admin tooling
- safer premium and entitlement operations
- better trust, disclosure, and review evidence for platform compliance
- more capable but still constrained summary layers built on top of deterministic signals
- a stronger local-first platform for communication-pattern support rather than a one-off “AI insight” feature

The long-term opportunity depends on trust, safety, and operational quality more than on adding speculative features quickly.

## Run And Setup

### Python analysis pipeline

```bash
python3 -m pip install --user -r requirements.txt
PYTHONPATH=src python3 -m vibesignal_ai analyze \
  --input tests/fixtures/relationship_chat_hardened.txt \
  --type whatsapp \
  --mode relationship_chat \
  --out ./outputs \
  --rights-asserted
```

Optional local packages can be installed separately for heavier integrations and provider work.

### Mobile app

```bash
cd mobile
npm install
npm test
```

Key mobile env vars are documented in [`mobile/README.md`](/Users/keith/Desktop/VibeSignal AI/mobile/README.md), including:

- `EXPO_PUBLIC_ENABLE_LOGGING`
- `EXPO_PUBLIC_API_URL`
- `EXPO_PUBLIC_REVENUECAT_IOS_API_KEY`
- `EXPO_PUBLIC_IOS_MONTHLY_PRODUCT_ID`
- `EXPO_PUBLIC_IOS_PREMIUM_ENTITLEMENT_ID`
- `EXPO_PUBLIC_SUBSCRIPTION_PRICE_DISPLAY`
- `EXPO_PUBLIC_PRIVACY_POLICY_URL`
- `EXPO_PUBLIC_TERMS_URL`

## Repo Truthfulness

This repo currently contains three different kinds of work:

### Built now

- deterministic analysis pipeline
- Expo mobile shell
- secure BYOK storage
- quota/paywall/subscription logic
- telemetry queueing and diagnostics
- test coverage for core mobile monetization and logging behavior

### Code-complete but unverified

- live iPhone sandbox purchase and restore
- final deployed backend acceptance of the mobile telemetry envelope
- final App Store legal-link and price-point configuration

### Planned / future

- fuller backend/admin observability in the deployed environment
- richer product surfaces after launch-stage validation
- broader platform maturity after the current mobile flow is proven on device

For the operational details behind that distinction, see:

- [`docs/handoff_status.md`](/Users/keith/Desktop/VibeSignal AI/docs/handoff_status.md)
- [`docs/prelaunch_readiness_checklist.md`](/Users/keith/Desktop/VibeSignal AI/docs/prelaunch_readiness_checklist.md)
- [`docs/iphone_sandbox_destruction_test_plan.md`](/Users/keith/Desktop/VibeSignal AI/docs/iphone_sandbox_destruction_test_plan.md)
