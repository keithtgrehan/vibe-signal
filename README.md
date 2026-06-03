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

Vibe Matching Engine v0 now adds a deterministic communication-fit layer:

- compatibility bands based on observable cue evidence
- safe inconsistency cues
- specificity drops
- answer-evasion patterns
- deterministic contradiction cues
- confidence in analysis quality, not confidence about truth, motive, attraction, or emotion

## Current Repo Reality
Built now:
- Expo mobile shell with an always-available local analysis path
- polished Expo mobile UI for match, cue evidence, feedback, and legal draft routes
- standalone Vite React web UI for the same backend-only match, cue evidence, feedback, and legal flows
- synthetic-first onboarding, private-input consent gates, low-signal fallback UI, and evidence-first result hierarchy
- deterministic local analysis and structured result rendering
- deterministic communication-fit matching engine with `/api/match`
- synthetic matching corpus and validator
- dataset/source-rights registry with commercial fail-closed validation
- research-only sklearn baseline on synthetic fixtures
- optional offline embedding experiment scaffold
- recent-analysis persistence plus copy/share actions
- optional BYOK provider validation and secure on-device storage when supported
- bounded mobile-to-backend event logging with retry, validation, and diagnostics
- quota, paywall, and RevenueCat-oriented mobile scaffolding
- privacy, provider-disclosure, and prelaunch-readiness documentation

Code-complete but still needing real-world proof:
- final real-device mobile QA against the deployed Render backend
- iPhone simulator/device runtime proof
- RevenueCat/App Store sandbox purchase and restore validation
- final legal review of privacy / terms / deletion / export / disclaimer copy

## Architecture Snapshot
- `mobile/`: Expo / React Native shell, provider setup, quota state, billing scaffolding, and event logging
- `web/`: standalone Vite / React browser frontend that can be deployed separately from the backend
- `src/vibesignal_ai/`: deterministic conversation analysis, contracts, providers, safety rules, and UI payload builders
- `docs/`: privacy flow, provider disclosure, backend contract notes, and execution-proof material
- `backend/`: FastAPI routes for health, analyze, match, feedback, legal copy, and event acceptance
- `data/vibe_matching/synthetic/`: synthetic-only match-pair fixture corpus
- `reports/vibe_matching/`: synthetic-only baseline and optional experiment reports
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
- [docs/privacy_policy_draft.md](docs/privacy_policy_draft.md) and [docs/terms_draft.md](docs/terms_draft.md) for draft app/site legal copy that still requires legal review
- [docs/data_deletion_request_draft.md](docs/data_deletion_request_draft.md) and [docs/data_export_request_draft.md](docs/data_export_request_draft.md) for closed-beta deletion/export readiness notes
- [docs/match_usage_consent_disclaimer.md](docs/match_usage_consent_disclaimer.md) for `/api/match` submission copy boundaries
- [docs/backend_deployment_readiness.md](docs/backend_deployment_readiness.md) for backend deployment checks, CORS configuration, and safe logging boundaries
- [docs/hosted_web_deployment.md](docs/hosted_web_deployment.md) for Vercel web deployment settings, Render CORS, smoke tests, and rollback
- [docs/closed_beta_qa_evidence.md](docs/closed_beta_qa_evidence.md) for metadata-only hosted backend/web QA evidence and blockers
- [docs/real_device_qa_runbook.md](docs/real_device_qa_runbook.md) for iPhone/Expo real-device QA flow
- [docs/ethical_engagement_principles.md](docs/ethical_engagement_principles.md) for ethical value-loop and anti-dark-pattern guardrails
- [docs/closed_beta_monitoring_incident_runbook.md](docs/closed_beta_monitoring_incident_runbook.md) for incident ownership, monitoring, and rollback
- [docs/deployment_smoke_tests.md](docs/deployment_smoke_tests.md) for repeatable local/deployed backend smoke tests before mobile beta use
- [docs/monitoring_no_raw_logs.md](docs/monitoring_no_raw_logs.md) for closed-beta monitoring checks and no-raw-log incident triggers
- [docs/final_closed_beta_launch_gate_report.md](docs/final_closed_beta_launch_gate_report.md) for the final closed-beta gate status, manual deploy QA sequence, and tester-invite decision rule
- [docs/closed_beta_readiness_checklist.md](docs/closed_beta_readiness_checklist.md) for the operator go/no-go checklist before tester invites
- [docs/device_qa_script.md](docs/device_qa_script.md) for real-device `/api/match`, legal-copy, and backend URL QA
- [docs/closed_beta_tester_instructions.md](docs/closed_beta_tester_instructions.md) for tester-facing boundaries and bug report format
- [docs/provider_disclosure_notes.md](docs/provider_disclosure_notes.md) for optional provider positioning
- [docs/legal_safe_output_policy.md](docs/legal_safe_output_policy.md) for wording and safety constraints
- [docs/datasets_rights.md](docs/datasets_rights.md) and [docs/dataset_attribution.md](docs/dataset_attribution.md) for metadata-only dataset rights gates and attribution posture
- [docs/research/nlp_engine_deep_research.md](docs/research/nlp_engine_deep_research.md) for deterministic cue/explainability research and known false-positive risks
- [docs/ios/testflight_launch_runbook.md](docs/ios/testflight_launch_runbook.md) and [docs/ios/real_device_qa_checklist.md](docs/ios/real_device_qa_checklist.md) for iOS/TestFlight readiness steps
- [docs/proof/closed_beta/launch_readiness.md](docs/proof/closed_beta/launch_readiness.md) for metadata-only launch gate proof
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
EXPO_PUBLIC_API_URL=https://vibe-signal.onrender.com npx expo start --web --clear
```

Standalone web UI:

```bash
cd web
npm install
VITE_API_BASE_URL=https://vibe-signal.onrender.com npm run dev
```

Optional backend contract check:

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://YOUR_BACKEND_HOST
cd mobile
npm run verify:backend -- --api-url https://YOUR_BACKEND_HOST --event state
```

Closed-beta operator flow:

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://YOUR_BACKEND_HOST
python scripts/smoke_test_deployed_backend.py --base-url https://YOUR_BACKEND_HOST --include-events
```

Then follow [docs/closed_beta_readiness_checklist.md](docs/closed_beta_readiness_checklist.md) and [docs/device_qa_script.md](docs/device_qa_script.md) before inviting testers. These checks prove only closed-beta connectivity and basic behavior, not production readiness, legal compliance, GDPR/CCPA readiness, model quality, or commercial data rights.

Browser-based local QA against the current Render/FastAPI backend also needs exact CORS origins configured in Render:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,http://localhost:19006,http://localhost:8081,http://localhost:5173
```

Do not use wildcard CORS origins. Add each future hosted web frontend origin explicitly.

Final closed-beta gate:

- Backend and hosted web are live, CORS is configured for the hosted web origin, and tester invites remain blocked until real-device QA, legal review, and P0 monitoring gates pass.

## Repo Truthfulness
Keep the story narrow:
- built now
- code-complete but not yet fully validated in live mobile/backend conditions
- future work only where explicitly labeled

No fake certainty. No unsupported claims.
