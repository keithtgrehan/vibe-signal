# Research To Execution Roadmap

Status date: 2026-06-08.

Purpose: convert the current research pile into small, safe future PRs. This is a planning document, not approval to train models, merge stale branches, add datasets, or change production runtime behavior.

## A. PR Hygiene / Close Superseded PRs

Goal: reduce stale open PR debt and document why superseded PRs were closed.

Likely files touched:

- `docs/control_room/open_pr_triage.md`
- `docs/control_room/research_recovery_log.md`
- PR comments on GitHub

Hard boundaries:

- Close only explicitly approved PRs.
- Do not delete branches.
- Do not merge or resolve conflicts.

Validation commands:

```bash
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
python -m pytest tests/test_public_copy_safety.py tests/test_private_data_hygiene.py -q
git diff --check
```

Merge gate: docs-only diff, clear PR closure rationale, no runtime changes.

## B. CORS Custom-Domain Fix And Smoke Proof

Goal: verify `https://www.vibe-signal.com` can call `/api/analyze` after the manual Render CORS update.

Likely files touched:

- `docs/ops/render_vercel_deployment_runbook.md`
- `docs/proof/closed_beta/production_analyze_timeout_fix.md`
- `docs/proof/closed_beta/backend_smoke_2026-06-03.md` or a new dated proof note

Hard boundaries:

- Keep this separate from research branches.
- Do not add wildcard CORS.
- Do not add analytics, auth, paywalls, trackers, or secret config.

Validation commands:

```bash
bash scripts/prod_smoke_custom_domain.sh
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
git diff --check
```

Merge gate: smoke proof with synthetic text only and no raw-content logs.

## C. Research Stash Audit, Docs-Only

Goal: recover useful ideas from local stashes without applying them to production branches.

Likely files touched:

- `docs/control_room/research_recovery_log.md`
- new docs under `docs/control_room/` if needed

Hard boundaries:

- Use `git stash branch` on a dedicated audit branch.
- Do not pop into `main` or demo branches.
- Do not commit raw/private data or generated artifacts.

Validation commands:

```bash
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
```

Merge gate: docs-only summary, no copied stash content beyond safe high-level direction.

## D. PR #46 / Private WhatsApp Research Audit, Docs-Only

Goal: recover safe high-level research direction from the superseded PR #46 branch.

Likely files touched:

- `docs/control_room/research_recovery_log.md`
- `docs/data/private_whatsapp_training_plan.md`
- `docs/research/model_training_plan/11_local_gold_evaluator_scaffold.md`

Hard boundaries:

- No raw private data.
- No production runtime changes.
- No model training.
- No generated reports or fixtures copied from the branch.

Validation commands:

```bash
python scripts/check_private_metadata_exposure.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
python -m pytest tests/test_private_data_hygiene.py -q
git diff --check
```

Merge gate: aggregate-only documentation, no branch merge, no raw/private content.

## E. Small Synthetic Hard-Negative Fixture Pack

Goal: add 50-200 synthetic rows that test cue false positives and unsafe-output boundaries.

Likely files touched:

- `data/synthetic/whatsapp/` or a new approved synthetic fixture path
- `tools/generate_synthetic_whatsapp_fixtures.py`
- `tests/test_synthetic_whatsapp_harness.py`
- `reports/engine_eval/` summary docs if generated reports are small and text-only

Hard boundaries:

- Synthetic-only.
- No private-inspired wording unless reviewed and safely abstracted.
- No real-world accuracy claims.

Validation commands:

```bash
python tools/run_synthetic_fixture_regression.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
python -m pytest tests/test_synthetic_whatsapp_harness.py tests/test_public_copy_safety.py -q
git diff --check
```

Merge gate: fixture rows are bounded, evidence-backed, and small enough for review.

## F. Active-Learning Queue, Neutral IDs Only

Goal: define local active-learning sampling without exposing message text.

Likely files touched:

- `docs/research/model_training_plan/04_label_taxonomy_gold_set.md`
- `docs/research/model_training_plan/11_local_gold_evaluator_scaffold.md`
- local-only tools under `tools/` only if they output neutral IDs and aggregate counts

Hard boundaries:

- Neutral row IDs only.
- No raw text, evidence text, reviewer notes, or source identifiers in committed reports.
- No CI over private rows.

Validation commands:

```bash
python scripts/check_private_metadata_exposure.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
python -m pytest tests/test_private_data_hygiene.py -q
git diff --check
```

Merge gate: local-only input path, ignored output path, aggregate/ID-only output.

## G. Local-Only Evaluator Improvements

Goal: improve validation and aggregate reporting for reviewed labels without training.

Likely files touched:

- `tools/validate_private_gold_labels.py`
- `tools/evaluate_private_gold_labels.py`
- `tests/test_private_gold_label_evaluator.py`
- `docs/research/model_training_plan/11_local_gold_evaluator_scaffold.md`

Hard boundaries:

- No model training.
- No private row text in logs.
- Reports stay ignored under restricted local paths.

Validation commands:

```bash
python -m pytest tests/test_private_gold_label_evaluator.py tests/test_private_data_hygiene.py -q
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
```

Merge gate: aggregate-only evaluator output and fail-closed private-data checks.

## H. Deterministic Cue Engine Improvements

Goal: improve observable cue detection while preserving safe-output boundaries.

Likely files touched:

- `src/vibesignal_ai/features/`
- `configs/vibe_cue_taxonomy.yml`
- `tests/test_*cue*.py`
- `tools/analyze_cue_false_positives.py`

Hard boundaries:

- No hidden-intent, deception, attraction, diagnosis, manipulation, neurotype, attachment-style, or outcome claims.
- Every new cue behavior needs hard negatives.

Validation commands:

```bash
python -m pytest tests/test_nlp_cue_contracts.py tests/test_hard_negative_precision.py tests/test_public_copy_safety.py -q
python scripts/check_public_copy_safety.py
git diff --check
```

Merge gate: cue behavior remains evidence-first and low-signal fallback remains intact.

## I. Classical Baseline Only After Reviewed-Label Thresholds

Goal: train an interpretable local baseline only after reviewed-label and rights thresholds are met.

Likely files touched:

- `docs/research/model_training_plan/*`
- future local-only tools under `tools/`
- tests for fail-closed source and output paths

Hard boundaries:

- Do not start until reviewed-label thresholds are met and approved.
- No production model training.
- No model artifacts committed.
- No external dataset rows without source-specific approval.

Validation commands:

```bash
python scripts/validate_vibe_training_sources.py
python scripts/check_vibe_restricted_artifacts.py --staged
python -m pytest tests/test_vibe_matching_training_gate.py tests/test_private_data_hygiene.py -q
git diff --check
```

Merge gate: explicit human approval, sufficient reviewed labels, aggregate-only reporting, no artifacts.

## J. iOS/TestFlight Proof

Goal: complete real-device QA and document beta-readiness blockers.

Likely files touched:

- `docs/ios/*`
- `docs/proof/closed_beta/real_device_qa_evidence_template.md`
- `docs/proof/closed_beta/closed_beta_go_no_go.md`

Hard boundaries:

- Do not claim App Store readiness until review is complete.
- No raw-content screenshots.
- Synthetic examples only in screenshots or demo evidence.

Validation commands:

```bash
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
```

Merge gate: real-device evidence recorded, legal/privacy caveats preserved.

## K. Legal/Privacy Review Package

Goal: package current drafts and data-flow notes for external or formal review.

Likely files touched:

- `docs/legal_privacy/*`
- `docs/privacy_data_flow.md`
- `docs/legal_safe_output_policy.md`
- `docs/data_rights_and_consent_policy.md`
- `docs/proof/closed_beta/legal_review_required.md`

Hard boundaries:

- Do not claim legal/privacy approval.
- Do not remove caveats.
- Do not add raw private content.

Validation commands:

```bash
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
python -m pytest tests/test_public_copy_safety.py tests/test_private_data_hygiene.py -q
git diff --check
```

Merge gate: review package is complete, caveated, and free of raw/private content.
