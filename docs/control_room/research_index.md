# Vibe Signal Research Index

Status date: 2026-06-08.

Purpose: one central map of Vibe Signal research, agent outputs, stale PRs, and safe next actions. This is a navigation document only. It is not legal approval, privacy approval, App Store readiness, production model-quality proof, or permission to train models.

Current recruiter baseline: PR #67, "Make Vibe Signal CEO-demo ready with neutral reviewer flow", is merged and is the current CEO-demo/recruiter surface.

Already merged/no action: PR #56, "Refresh README for recruiter demo and n8n ops workflow", is merged and requires no action.

## Operating Boundaries

- No raw private chats, tester messages, raw-message fixtures, raw-content screenshots, external datasets, model artifacts, embeddings, vector stores, or training outputs belong in this control-room pass.
- Public and recruiter-facing surfaces must stay company-neutral.
- Vibe Signal reviews observable wording patterns, not hidden intent, attraction, deception, diagnosis, manipulation, neurotype, attachment style, or relationship outcomes.
- Synthetic checks prove product flow, output-contract behavior, and safety behavior under controlled conditions. They are not real-world accuracy claims.
- Research branches and stashes are future audit sources only. Do not merge them directly into production or demo branches.

## Product / GTM Positioning

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `README.md`; `docs/recruiter_readiness/project_summary.md`; `docs/recruiter_readiness/repo_tour.md`; `docs/control_room/market_engine_strategy_summary.md`; `docs/claims_matrix.md` | Merged; PR #67 is current recruiter baseline | Keep README compact and point deeper research here | Do not add company-specific positioning to public generic docs | Recruiter-facing |

## UI/UX And Trust-First Design

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/design/simple_ui_copy_system.md`; `docs/design/simple_ui_information_architecture.md`; `docs/design/ui_component_inventory.md`; `docs/design/ui_style_notes.md`; `docs/research/ui_minimal_redesign/*`; `docs/research/ui_ux/*`; PR #66 filename list | PR #67 shipped the useful CEO-demo subset; PR #66 was closed as superseded in this cleanup run | Recover any remaining accessibility or reviewer-flow ideas through a small branch from current `main` | Do not merge PR #66 as-is; it is broad, conflicted, and had an incomplete PR body | Mixed: recruiter-facing only after extraction |

## NLP Cue Taxonomy And Deterministic Engine

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/vibe_cue_taxonomy.md`; `configs/vibe_cue_taxonomy.yml`; `docs/research/observable_cue_taxonomy.md`; `docs/research/cue_preconditions_v2.md`; `docs/research/blocked_inferences_and_false_positive_risks.md`; `src/vibesignal_ai/features/`; `tests/test_*cue*.py` | Merged deterministic-first engine direction | Add focused cue improvements only with evidence-span tests and hard-negative tests | Do not convert cue labels into claims about motives or outcomes | Research-only unless surfaced through safe UI copy |

## Model Training Research Plan

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/research/model_training_plan/00_executive_summary.md` through `11_local_gold_evaluator_scaffold.md`; `configs/vibe_training_sources.example.yml`; `scripts/validate_vibe_training_sources.py`; `tools/validate_training_sources.py` | Research plan merged; training remains blocked | Keep as roadmap until reviewed-label thresholds, rights review, privacy review, and safety gates pass | No production model training; no external dataset rows; no model artifacts | Research-only |

## Synthetic Fixtures / Hard Negatives

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `tools/generate_synthetic_whatsapp_fixtures.py`; `tools/run_synthetic_fixture_regression.py`; `data/synthetic/whatsapp/`; `docs/research/synthetic_fixture_plan.md`; `docs/research/synthetic_whatsapp_regression_method.md`; `reports/engine_eval/` | Merged synthetic regression harness | Add a small 50-200 row hard-negative pack in a future branch if needed | Synthetic-only coverage is not real-world accuracy | Research-only, with summarized caveats recruiter-facing |

## Private WhatsApp / Local-Only Research Pipeline

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/data/private_whatsapp_training_plan.md`; `docs/proof/closed_beta/private_whatsapp_training_pipeline.md`; `tools/prepare_private_label_review.py`; `tools/validate_private_gold_labels.py`; `tools/evaluate_private_gold_labels.py`; PR #44; PR #46 filename list | Research-only; PR #46 was closed as superseded in this cleanup run; PR #44 remains extract-only | Future docs-only audit branch should recover aggregate-only workflow direction from current `main` | Do not merge raw/private pipelines wholesale; no raw private content in tracked files; no training scripts without review gates | Research-only |

## Gold Label Evaluator

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/research/model_training_plan/11_local_gold_evaluator_scaffold.md`; `tools/validate_private_gold_labels.py`; `tools/evaluate_private_gold_labels.py`; `tests/test_private_gold_label_evaluator.py`; PR #56 merged context | Merged scaffold direction; local-only | Use aggregate-only reports under restricted ignored paths | Reviewed labels are pending/research-gated; no model-quality claims | Research-only |

## n8n Beta Ops

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `ops/n8n/README.md`; `ops/n8n/docs/n8n_beta_ops_runbook.md`; `ops/n8n/docs/interview_demo_script.md`; `ops/n8n/payloads/*.json`; `docs/proof/closed_beta/n8n_beta_ops_demo.md`; PR #56 | Merged ops/demo scaffold | Keep n8n metadata-only and optional | n8n is not the AI engine and must not receive raw private chat content | Mixed: recruiter-facing at workflow level, research-only for ops details |

## iOS/TestFlight Readiness

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/ios/*`; `docs/proof/closed_beta/manual_qa_required.md`; `docs/proof/closed_beta/real_device_qa_evidence_template.md`; `docs/proof/closed_beta/closed_beta_go_no_go.md`; `docs/agents/agent_5_ios_testflight_launch.md` | Pending manual QA and review | Run real-device QA and record evidence before wider beta invites | Do not claim App Store or TestFlight readiness until proven | Mostly research/ops; caveats recruiter-facing |

## Deployment/Smoke/CORS

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/ops/render_vercel_deployment_runbook.md`; `docs/deployment_smoke_tests.md`; `scripts/prod_smoke_custom_domain.sh`; `docs/control_room/prod_smoke_deploy_status_automation_handoff.md`; PR #45 | Custom-domain CORS remains manual/pending; PR #45 was Replit-specific and superseded | Handle custom-domain CORS in a narrow deployment PR or manual Render update, then rerun smoke | Do not fix CORS in recruiter/docs cleanup PRs | Recruiter-facing only as deployment caveat |

## Recruiter/Demo Readiness

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| PR #67; `README.md`; `docs/recruiter_readiness/project_summary.md`; `docs/recruiter_readiness/repo_tour.md`; `docs/recruiter_readiness/current_pr_status.md` | Merged; current baseline | Keep first-review path short: live app, synthetic demo, evidence phrases, safe next step, docs | Do not overclaim production readiness or model accuracy | Recruiter-facing |

## Company-Specific Prep Docs

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/recruiter_readiness/company_specific/delvo_relevance.md` | Merged and isolated | Keep company-specific prep out of public generic docs and homepage | Do not duplicate company-specific content into README or generic recruiter docs | Interview-prep only |

## Open PR / Stale Branch Notes

| Source docs/files | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `docs/control_room/open_pr_triage.md`; `docs/ops/open_pr_debt_triage.md`; `docs/recruiter_readiness/current_pr_status.md`; PR #40, #41, #42, #44, #45, #46, #66 | Superseded PRs documented and closed through recruiter-readiness polish | Keep future research recovery on small branches from current `main` | Do not close unrelated future PRs without a new instruction | Research-only, with concise recruiter summary if needed |

## Stashes / Local-Only Work Notes

Visible from `git stash list --date=local` only. No stash contents were inspected, applied, popped, merged, or copied.

| Visible stash note | Status | Safe next action | Warning | Audience |
| --- | --- | --- | --- | --- |
| `On codex/100k-synthetic-relationship-dynamics-fixtures: auto-stash-before-ceo-demo-branch-20260608-153344` | Local-only | Audit later on a dedicated branch if needed | Do not pop into `main`, CEO-demo branches, or production branches | Research-only |
| `On codex/web-d2c-redesign-safe-scanner: temp unrelated copy safety web dirty files before private workbook review` | Local-only | Audit later only if UI/copy research is still needed | Do not mix with reviewer or production branches | Research-only |
| `On codex/whatsapp-dynamics-research-prototype: temp replit cors frontend dirty changes before private whatsapp work` | Local-only | Audit later only after PR #46/#45 decisions are settled | Do not mix Replit/CORS/private research work | Research-only |
| `On docs/ab-test-feedback-automation: wip ab test feedback automation docs` | Local-only | Audit later if A/B governance remains useful | Do not introduce analytics/tracking assumptions | Research-only |
