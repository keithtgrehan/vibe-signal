# Vibe Signal Demo Script

## 60-second CEO version

"I wanted to show something real rather than just talk about AI.

Vibe Signal is a small product I built that takes messy communication and turns it into structured, evidence-backed signals.

The key thing is not the communication domain. It is the system pattern: messy input, bounded analysis, evidence extraction, safe outputs, and a usable product surface.

The demo is intentionally synthetic and bounded. It reviews wording patterns, not people's motives.

For a target company, I would apply the same system pattern to their domain: preserve provenance, show why a recommendation was made, keep the human decision-maker in control, and turn messy data into usable action."

## 30-second recruiter version

"I built a live AI product surface, not just a concept.

It has frontend, backend, deterministic cue logic, evidence-backed output, safety boundaries, and recruiter-friendly docs.

The demo is synthetic and bounded; it does not claim real-world model accuracy."

## 90-second CTO / technical version

"The web frontend is hosted on Vercel and the backend is FastAPI on Render.

The product is deterministic-first: it runs cue logic, creates evidence objects, and renders safe result cards rather than treating a model response as truth.

The first demo path is synthetic. Custom input is consent-gated, backend-backed, and designed around no raw-chat persistence. Feedback is metadata-only.

The repo includes public-copy, no-raw-content, and restricted-artifact scanners, plus tests, synthetic regression tooling, and production smoke scripts.

The current caveat is deployment-specific: custom-domain private analysis may need CORS/deploy verification. The synthetic demo and product logic remain the recommended first path."

## n8n / automation version

"The workflow pattern is product event -> metadata payload -> workflow routing -> human follow-up.

n8n is optional operations automation, not the analysis engine.

The safe role for automation is routing metadata-only events such as feedback categories, safety-review flags, backend health checks, or review queues. Raw private messages should not be sent through automation without explicit future review."

## What to click

1. Open [https://www.vibe-signal.com](https://www.vibe-signal.com).
2. Click the synthetic demo.
3. Show evidence phrases.
4. Show signal/cue breakdown.
5. Show safe next step.
6. Show limits/non-claims.
7. Point to README / project summary / repo tour.

## What to point out in the repo

- README reviewer quick start.
- `docs/recruiter_readiness/project_summary.md`.
- `docs/recruiter_readiness/repo_tour.md`.
- `docs/recruiter_readiness/architecture_overview.md`.
- `docs/control_room/research_index.md`.
- Safety scanners.
- Tests.
- n8n beta ops docs.

## If CORS/private analyze fails

- Use the synthetic demo.
- Say private custom analysis is backend-backed and custom-domain CORS/deploy verification is separate.
- Do not hide it.
- Frame it as deployment-config verification, not product logic failure.

## Do not say

- Do not say it detects intent.
- Do not say it detects attraction.
- Do not say it detects deception or cheating.
- Do not say it is therapy or diagnosis.
- Do not say it infers neurotype or attachment style.
- Do not say it gives manipulation advice.
- Do not say it predicts relationship outcomes.
- Do not say it is legally/privacy reviewed.
- Do not say synthetic demos prove real-world accuracy.
- Do not say n8n is the analysis engine.
