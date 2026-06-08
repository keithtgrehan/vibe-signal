# Vibe Signal

Vibe Signal is a privacy-conscious communication-support app that highlights observable wording patterns such as clarity, ambiguity, pressure, reassurance, and repair opportunities.

The product is built around a deterministic-first cue engine, evidence-first result cards, consent-gated private input, and strict copy/safety boundaries. It helps users review wording, not infer private motives.

## CEO / Reviewer Quick Start

1. Open [https://www.vibe-signal.com](https://www.vibe-signal.com).
2. Run the synthetic demo.
3. Review evidence phrases and safe next step.
4. Read [docs/recruiter_readiness/project_summary.md](docs/recruiter_readiness/project_summary.md).
5. Read [docs/recruiter_readiness/repo_tour.md](docs/recruiter_readiness/repo_tour.md).

What to look for:

- shipped frontend + backend
- deterministic-first AI product logic
- evidence-backed outputs
- privacy/safety constraints
- evaluation and regression discipline

Important caveat: Synthetic demo and regression checks prove product flow, output-contract behavior, and safety behavior under controlled conditions. They are not real-world accuracy claims or legal/privacy approval.

## Reviewer Links

- Live demo: [https://www.vibe-signal.com](https://www.vibe-signal.com)
- Project summary: [docs/recruiter_readiness/project_summary.md](docs/recruiter_readiness/project_summary.md)
- Repo tour: [docs/recruiter_readiness/repo_tour.md](docs/recruiter_readiness/repo_tour.md)
- Architecture overview: [README.md#architecture-overview](#architecture-overview)
- Evaluation caveat: [docs/recruiter_readiness/project_summary.md#evaluation-story](docs/recruiter_readiness/project_summary.md#evaluation-story)
- Safety policy: [docs/legal_safe_output_policy.md](docs/legal_safe_output_policy.md)
- Research/control-room index: [docs/control_room/research_index.md](docs/control_room/research_index.md)

## Live Demo

- Primary web app: [https://www.vibe-signal.com](https://www.vibe-signal.com)
- Apex redirect: [https://vibe-signal.com](https://vibe-signal.com) -> [https://www.vibe-signal.com](https://www.vibe-signal.com)
- Fallback/preview web app: [https://vibe-signal.vercel.app](https://vibe-signal.vercel.app)
- Backend health: [https://vibe-signal.onrender.com/healthz](https://vibe-signal.onrender.com/healthz)
- Backend status metadata: [https://vibe-signal.onrender.com/api/status](https://vibe-signal.onrender.com/api/status)

Vercel deploys the frontend and Render deploys the backend separately. Static legal pages render from the web bundle and work without Render. Private custom analysis calls the Render backend.

## 60-Second Demo Path

1. Open [https://www.vibe-signal.com](https://www.vibe-signal.com).
2. Run the synthetic demo first.
3. Review the evidence phrases, signal cards, limits, and safe next step.
4. Try short custom text only if you have permission.
5. Do not paste sensitive/private third-party content.

The synthetic demo is the intended first-success path because it runs locally in the frontend and does not depend on Render cold starts, CORS, or backend deploy timing.

## What It Does

- Highlights observable communication cues such as directness, ambiguity, pressure wording, reassurance, cognitive load, and repair openings.
- Shows evidence phrases from the words provided.
- Gives safe clarification, boundary, or repair-oriented next steps.
- Uses a low-signal fallback when text is too short or context-light.
- Keeps the synthetic demo local to the web bundle.
- Supports metadata-only feedback.
- Keeps legal pages static-first so public draft legal content remains visible even if Render is unavailable.

## What It Does Not Do

Vibe Signal stays inside communication-support boundaries:

- no hidden intent
- no attraction prediction
- no deception or cheating detection
- no diagnosis or therapy
- no neurotype or attachment labels
- no manipulation advice
- no relationship-outcome prediction
- no model-accuracy claim from synthetic tests
- no final legal, privacy, App Store, or AI-law review claim

## Why This Repo Matters

For recruiters, hiring managers, technical interviewers, product/AI reviewers, beta testers, and future collaborators, this repo is a proof-of-work project across:

- AI product thinking
- trust/safety UX
- deterministic NLP cue design
- full-stack deployment
- CI/testing discipline
- privacy-conscious architecture
- operational debugging
- legal-readiness process
- Codex-driven development workflow

The interesting part is not a single model call. It is the full product system around bounded claims, observable evidence, recovery paths, deploy operations, and reviewable safety gates.

## Architecture Overview

| Path | Role |
| --- | --- |
| `web/` | Vite/React frontend on Vercel with the Scanner-style UI, local synthetic demo, static-first legal pages, consent-gated custom analyze, and metadata-only feedback. |
| `backend/` | FastAPI backend on Render for private custom analysis, health/status routes, feedback, and legal API parity. |
| `src/vibesignal_ai/` | Deterministic-first cue engine, interfaces, safety rules, evidence objects, summaries, and blocked-output boundaries. |
| `mobile/` | Expo mobile app shell, onboarding, consent, matching/results flow, legal screens, and Render backend configuration. |
| `tools/` | Synthetic fixture generation, regression runners, evaluation utilities, and reviewer packet scaffolding. |
| `docs/` | Product, safety, legal-readiness, deployment, data-rights, reviewer, and closed-beta evidence docs. |
| `ops/n8n/` | Optional workflow automation artifacts for beta operations and demo workflows. |
| `scripts/` | Public-copy safety, no-raw-content, restricted-artifact, deployment smoke, and local validation scripts. |
| `tests/` | Python test suite for backend, safety, docs, engine interfaces, evaluation gates, and operating assumptions. |

## How n8n Fits In

n8n is an optional operations/workflow automation layer around the product. It is not the core product engine and is not required for analysis. n8n does not replace the deterministic engine.

The intended n8n use cases are operational:

- beta tester intake workflow
- smoke-check/report reminders
- feedback triage routing
- issue/incident notification
- recruiter/demo workflow automation
- future no-raw-content operational workflows

n8n should not receive raw private chat content unless a future rights-reviewed workflow explicitly allows it. The current repo includes `ops/n8n/` artifacts and runbooks for metadata-only beta operations and demo support, not runtime message analysis.

## Deployment Model

- Vercel builds and serves `web/`.
- Render runs the FastAPI backend at [https://vibe-signal.onrender.com](https://vibe-signal.onrender.com).
- The custom web domain requires the Render CORS allowlist to include `https://www.vibe-signal.com` and `https://vibe-signal.com`.
- Static legal pages work without Render because the current legal copy is bundled into the frontend.
- Private analyze requires the Render backend.
- Synthetic demo results are local and should keep working when Render is cold, stale, or unreachable.
- `scripts/prod_smoke_custom_domain.sh` verifies the production state with synthetic text only.

Current expected CORS origins:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://www.vibe-signal.com,https://vibe-signal.com,https://vibe-signal.vercel.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:19006,http://localhost:8081
```

See [docs/ops/render_vercel_deployment_runbook.md](docs/ops/render_vercel_deployment_runbook.md) for Render/Vercel deploy and smoke-test details.

## Current Status

- Scanner redesign merged.
- Custom domain live at [https://www.vibe-signal.com](https://www.vibe-signal.com).
- Static legal pages merged; legal pages remain `draft_requires_legal_review`.
- Timeout/cancel recovery merged for custom analyze.
- Production API-base routing and CORS config are in repo.
- Production smoke script added and hardened.
- Verify production smoke before a live demo; Render custom-domain CORS may require a latest-main deploy if the smoke script reports an OPTIONS failure.
- Real-device iPhone/TestFlight QA is still required before wider beta invites.
- Legal/privacy review is still required before wider beta invites.

Closed-beta gate status is tracked in [docs/proof/closed_beta/closed_beta_go_no_go.md](docs/proof/closed_beta/closed_beta_go_no_go.md).

## Safety And Privacy Posture

- No raw chat persistence by design.
- Metadata-only feedback.
- No analytics, cookies, or tracking added.
- Public-copy safety checks block unsafe product claims.
- No-raw-content checks guard against raw private message leakage.
- Restricted-artifact checks block unsafe datasets, vectors, model artifacts, and raw-message files.
- Dataset/training rights gates keep external training paths blocked until reviewed.
- Legal pages are draft-only and pending legal review.
- Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.

## Local Development

Backend:

```bash
python3 -m pip install -r requirements.txt
PYTHONPATH=src python -m uvicorn backend.app:app --host 0.0.0.0 --port 5050
```

Web:

```bash
cd web
npm install
VITE_API_BASE_URL=http://localhost:5050 npm run dev
```

Tests:

```bash
python -m pytest
cd web && npm test && npm run build
```

Production smoke:

```bash
bash scripts/prod_smoke_custom_domain.sh
```

The smoke script uses synthetic text only. Treat any CORS or `/api/legal/*` backend-parity failure as a deploy verification item; frontend legal pages should still work from the Vercel bundle.

## Validation Commands

```bash
python scripts/check_public_copy_safety.py
python -m pytest tests/test_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
cd web && npm test && npm run build
python -m pytest
bash scripts/prod_smoke_custom_domain.sh
```

## Roadmap

- Verify production smoke before demos and beta invites.
- Beta tester onboarding.
- Feedback triage workflow.
- iOS/TestFlight real-device QA.
- `privacy@vibe-signal.com`.
- Legal review.
- More synthetic fixtures and reviewer workflow.
- Optional n8n operational automations.

## Reviewer Starting Points

- [docs/recruiter_readiness/project_summary.md](docs/recruiter_readiness/project_summary.md)
- [docs/recruiter_readiness/repo_tour.md](docs/recruiter_readiness/repo_tour.md)
- [docs/proof/closed_beta/closed_beta_go_no_go.md](docs/proof/closed_beta/closed_beta_go_no_go.md)
- [docs/privacy_data_flow.md](docs/privacy_data_flow.md)
- [docs/legal_safe_output_policy.md](docs/legal_safe_output_policy.md)
- [docs/ethical_engagement_principles.md](docs/ethical_engagement_principles.md)
- [docs/proof/closed_beta/n8n_beta_ops_demo.md](docs/proof/closed_beta/n8n_beta_ops_demo.md)
