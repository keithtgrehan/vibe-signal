# Vibe Signal

Vibe Signal is a privacy-conscious communication-support app that highlights observable message patterns like clarity, ambiguity, pressure, reassurance, and repair opportunities.

It is built around a deterministic-first cue engine, evidence-first result objects, and safety gates that keep the product focused on visible wording rather than private motives or unsupported relationship claims.

## Live Demo

- Web app: [https://vibe-signal.vercel.app](https://vibe-signal.vercel.app)
- Backend health: [https://vibe-signal.onrender.com/healthz](https://vibe-signal.onrender.com/healthz)
- Backend status metadata: [https://vibe-signal.onrender.com/api/status](https://vibe-signal.onrender.com/api/status)

The `/api/status` route exposes only allowlisted deploy metadata such as `git_commit`, `deploy_version`, `build_timestamp`, and `service_revision` when those environment variables are configured. If Render metadata is not configured, deployed-version confidence remains limited.

## Quick Demo Path

1. Open the hosted web app.
2. Run a synthetic demo card first.
3. Inspect the result hierarchy: summary, signal strength, cue labels, evidence phrases, cannot-infer limits, and safe next step.
4. Review the local engine reports under [reports/engine_eval](reports/engine_eval).
5. For mobile preview, run Expo with `EXPO_PUBLIC_API_URL=https://vibe-signal.onrender.com`.

Synthetic examples are intentionally the first-success path. Do not paste private messages unless you have permission and understand the consent warnings.

## What It Does

- Highlights observable communication cues such as direct asks, ambiguity, urgency, reassurance, pressure, boundary pressure, cognitive load, unanswered asks, conflict escalation, and repair opportunities.
- Shows evidence spans and safe phrases instead of summary-only output.
- Uses low-signal fallback when text is too short or context-light.
- Explains what the result cannot infer.
- Suggests safer clarification, boundary, or repair-oriented next steps.
- Supports synthetic demo-first web and mobile testing.
- Keeps dataset/training paths behind rights gates and commercial fail-closed checks.

## What It Does Not Do

Vibe Signal does not:

- detect cheating
- detect hidden intent
- predict attraction
- detect lying
- diagnose people
- provide therapy or mental-health assessment
- infer attachment style or neurotype
- manipulate people or optimize persuasion
- claim real-world accuracy from synthetic fixtures
- claim production readiness, legal compliance, or App Store approval

## Architecture

| Layer | What is in this repo |
| --- | --- |
| Web frontend | `web/` Vite/React app with trust-first landing, synthetic demo flow, evidence-first result cards, legal links, and metadata-only feedback |
| Mobile app | `mobile/` Expo app with polished onboarding, consent gate, analysis/results flow, legal screens, and Render backend configuration |
| Backend API | `backend/` FastAPI routes for health, status, analyze, match, feedback, legal copy, and safe event handling |
| Deterministic engine | `src/vibesignal_ai/` cue taxonomy, matching logic, evidence objects, contracts, safety rules, and output explainers |
| Evaluation harness | `tools/`, `data/synthetic/`, and `reports/engine_eval/` synthetic WhatsApp fixtures, API regression runners, hard-negative/red-team splits, bootstrap metrics, and human-review packet scaffolds |
| Safety gates | public-copy scanner, no-raw-content scanner, restricted-artifact checks, safe-output blocker, consent copy, and dataset-rights validation |

## Engine Status

| Area | Status |
| --- | --- |
| Deterministic cue engine | Implemented |
| Evidence-first result objects | Implemented |
| Safe-output blocker | Implemented |
| Low-signal fallback | Implemented |
| 1k synthetic API regression | Passed locally after PR #22 and PR #25 verification |
| 10k split-aware synthetic evaluation | Implemented in PR #27; hardening active in PR #29 |
| Hard-negative evaluation | Implemented; hard-negative precision hardening active in PR #29 |
| Red-team safety checks | Implemented |
| Human-review packet | Prepared |
| Human-reviewed labels | Pending |
| External dataset training | Blocked by rights gate |
| Real-world accuracy claims | Not claimed |

## Evaluation Status

Current `main` includes the 10k split-aware evaluation system from PR #27. PR #29 is in active review and hardens that system with the latest local synthetic regression reports:

- Evidence completeness: `4574/5000` -> `5000/5000`
- Hard-negative unexpected cues: `334` -> `0`
- Overall bootstrap micro P/R/F1: `0.5732 / 0.6827 / 0.6232` -> `0.6646 / 0.947 / 0.7811`
- Overall bootstrap macro P/R/F1: `0.6494 / 0.5483 / 0.7223` -> `0.7998 / 0.9379 / 0.8278`
- Unsafe-output block: `5000/5000`
- Red-team safety: `500/500`

These are bootstrap-only synthetic regression metrics. They are not human-reviewed accuracy, model-quality proof, validation, or production-readiness claims.

Start with:

- [reports/engine_eval/README.md](reports/engine_eval/README.md)
- [reports/engine_eval/10k_precision_hardening_comparison.md](reports/engine_eval/10k_precision_hardening_comparison.md)
- [reports/engine_eval/metric_calculation_audit.md](reports/engine_eval/metric_calculation_audit.md)
- [reports/engine_eval/evidence_gap_analysis_10k.md](reports/engine_eval/evidence_gap_analysis_10k.md)
- [reports/engine_eval/hard_negative_false_positive_reduction.md](reports/engine_eval/hard_negative_false_positive_reduction.md)

## UI Status

Recent UI work restored and polished the web/mobile experience while keeping the backend and deterministic contracts as the source of truth:

- trust-first landing page
- synthetic demo-first flow
- evidence-first result cards
- consent-gated private input warnings
- clearer loading/error/low-signal states
- metadata-only feedback
- legal/disclaimer visibility
- mobile matching flow and Expo web preview
- accessibility and focus polish from the trust-first UI work

The UI should present Vibe Signal as communication-support tooling, not as a dating wingman, relationship predictor, or hidden-truth engine.

## Safety And Privacy Posture

- Public-copy scanner checks web/mobile/backend/docs surfaces for unsafe public claims.
- No-raw-content scanner checks for raw message logging or persistence risks.
- Restricted-artifact checks block raw external datasets, model artifacts, vectors, and other unsafe files.
- Private input is consent-gated.
- Docs and reports use synthetic examples only.
- Feedback paths are metadata-only.
- Training/source registries are rights-gated and commercial fail-closed.
- No raw private chats are used for training, fixtures, docs, or reports.

## Current Limitations

- Not production launched.
- Not App Store released.
- Real-device iPhone/TestFlight QA is still required before tester invites.
- Legal/privacy review is still required before tester invites.
- Human-reviewed cue labels are pending.
- Synthetic fixtures are regression coverage, not real-world validation.
- No real-world accuracy or model-quality claim is made.
- Deployed backend version proof depends on Render environment variables populating `/api/status` metadata.
- Closed-beta tester invites remain blocked until real-device QA, legal/privacy review, and P0 monitoring gates pass.

## Repo Tour For Reviewers

- [docs/recruiter_readiness/project_summary.md](docs/recruiter_readiness/project_summary.md) explains the product and engineering story.
- [docs/recruiter_readiness/repo_tour.md](docs/recruiter_readiness/repo_tour.md) gives a fast walkthrough.
- [docs/recruiter_readiness/current_pr_status.md](docs/recruiter_readiness/current_pr_status.md) summarizes recent PR state and merge order.
- [docs/privacy_data_flow.md](docs/privacy_data_flow.md) documents privacy boundaries.
- [docs/legal_safe_output_policy.md](docs/legal_safe_output_policy.md) defines blocked claims and safe output language.
- [docs/ethical_engagement_principles.md](docs/ethical_engagement_principles.md) documents anti-dark-pattern guardrails.
- [docs/datasets_rights.md](docs/datasets_rights.md) and [docs/dataset_attribution.md](docs/dataset_attribution.md) document dataset-rights posture.
- [docs/research/nlp_engine_deep_research.md](docs/research/nlp_engine_deep_research.md) summarizes deterministic NLP/explainability research.
- [docs/proof/closed_beta/closed_beta_go_no_go.md](docs/proof/closed_beta/closed_beta_go_no_go.md) tracks launch-gate status.

## Running Locally

Python/backend:

```bash
python3 -m pip install -r requirements.txt
python -m pytest -q
PYTHONPATH=src python -m uvicorn backend.app:app --host 0.0.0.0 --port 5050
```

Web:

```bash
cd web
npm install
VITE_API_BASE_URL=https://vibe-signal.onrender.com npm run dev
npm test
npm run build
```

Mobile:

```bash
cd mobile
npm install
EXPO_PUBLIC_API_URL=https://vibe-signal.onrender.com npx expo start --web --clear
npm test
npx expo config --type public
```

Engine evaluation:

```bash
python tools/generate_synthetic_whatsapp_fixtures.py --messages 10000 --splits dev=6000,hard_negative=2000,heldout=1000,red_team=1000 --no-api
VIBE_SIGNAL_API_URL=http://localhost:5050 python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/dev/conversations.jsonl --split dev
VIBE_SIGNAL_API_URL=http://localhost:5050 python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/hard_negative/conversations.jsonl --split hard_negative
VIBE_SIGNAL_API_URL=http://localhost:5050 python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/heldout/conversations.jsonl --split heldout
VIBE_SIGNAL_API_URL=http://localhost:5050 python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/red_team/conversations.jsonl --split red_team
python tools/evaluate_reviewed_cue_labels.py --bootstrap --all-splits
```

Safety checks:

```bash
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
```

## CORS For Local Browser QA

Browser-based local QA against the current Render/FastAPI backend needs exact CORS origins configured in Render:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,http://localhost:19006,http://localhost:8081,http://localhost:5173
```

Do not use wildcard CORS origins. Add each future hosted web frontend origin explicitly.

## What This Project Demonstrates

Vibe Signal is a full-stack AI product engineering case study:

- deterministic NLP/cue-system design without overclaiming
- evidence-first UX and explainable output contracts
- web, mobile, and backend integration
- privacy-conscious product boundaries
- anti-dark-pattern product judgment
- synthetic regression, hard-negative testing, and red-team safety checks
- dataset-rights gates and no-raw-artifact discipline
- closed-beta launch-gate thinking

The strongest story is disciplined product engineering under safety constraints: narrow claims, visible evidence, testable contracts, and honest limits.
