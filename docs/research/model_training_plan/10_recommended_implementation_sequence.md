# Recommended Implementation Sequence

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. Do not implement training until this plan is reviewed and approved.

## Phase 0 - Legal/Data-Rights Gate

Goal: make source eligibility explicit and fail-closed.

Inputs:

- existing source registry examples;
- privacy/license research;
- private metadata guardrails.

Outputs:

- source registry schema update;
- dataset-use decision table;
- legal/privacy/harm review checklist.

Scripts to build later:

- `scripts/validate_training_source_registry.py`.

Tests:

- unknown source defaults blocked;
- unknown enum values fail validation;
- stale or expired approvals fail validation;
- non-primary license or terms URLs fail validation when primary sources are available;
- contradictory registry booleans fail validation;
- allowed uses cannot exceed license, terms, privacy, DPA, transfer, or harm-review approvals;
- missing license blocks product training;
- non-commercial source blocks product training;
- private source blocks provider upload and CI.

Privacy constraints:

- no private rows read;
- no dataset downloads;
- no provider calls.

Stop conditions:

- source license unclear;
- sensitive domain without harm review;
- private metadata appears in tracked files.

Review checkpoint:

- Keith/user reviews registry fields and approval workflow.

## Phase 1 - Label Schema Plus Local Gold Evaluator

Goal: turn the approximately 30 reviewed rows into a local-only evaluator smoke test without training.

Inputs:

- local-only private review rows;
- schema from `04_label_taxonomy_gold_set.md`.

Outputs:

- aggregate local metrics only;
- schema QA report;
- cue confusion notes without row text.

Scripts to build later:

- `scripts/eval_local_gold.py`.

Tests:

- script refuses tracked output paths;
- script requires explicit local restricted input;
- report contains counts only;
- no raw text in report.

Privacy constraints:

- local-only execution;
- no CI over private data;
- no row text in logs.

Stop conditions:

- raw text would be printed or written to a tracked path;
- row count too low for a metric claim.

Review checkpoint:

- approve schema changes before more labeling.

## Phase 2 - Synthetic Fixture Expansion

Goal: increase safe regression coverage.

Inputs:

- cue taxonomy;
- synthetic generation plan;
- blocked output registry.

Outputs:

- synthetic fixture pack;
- hard-negative pack;
- red-team prompt/output tests.

Scripts to build later:

- `scripts/generate_synthetic_fixture_pack.py` only if needed.

Tests:

- expected cue labels;
- evidence spans;
- low-signal fallback;
- unsafe output blocks.

Privacy constraints:

- no private examples in prompts;
- no private-derived paraphrases.

Stop conditions:

- fixture resembles private row wording;
- fixture encourages blocked use.

Review checkpoint:

- human review of synthetic fixture quality.

## Phase 3 - Weak-Label Baseline

Goal: measure deterministic cue functions as weak labels against human review.

Inputs:

- deterministic engine outputs;
- local gold aggregate evaluator;
- synthetic fixtures.

Outputs:

- coverage/overlap/conflict metrics;
- weak-label calibration notes;
- active-learning queue by neutral row ID.

Scripts to build later:

- `scripts/compare_weak_supervision.py`.

Tests:

- aggregate output only;
- conflict counts by cue;
- no raw content in logs.

Privacy constraints:

- local-only private rows;
- no provider upload;
- no CI private run.

Stop conditions:

- weak labels are treated as gold;
- output includes raw private content.

Review checkpoint:

- decide which label functions need tuning.

## Phase 4 - Classical Local Baseline

Goal: train first local-only prototype after enough labels exist.

Inputs:

- 600-1,000 reviewed rows for broad cue-family prediction;
- at least 80-100 positives per primary cue family;
- hard negatives and low-signal rows.

Outputs:

- local-only prototype model;
- aggregate eval report;
- model card draft without artifact.

Scripts to build later:

- `scripts/train_local_classical_baseline.py`.
- `scripts/report_model_card_metrics.py`.

Tests:

- training refuses insufficient labels;
- artifacts write only to ignored local path;
- report is aggregate/redacted;
- safety tests pass.

Privacy constraints:

- no committed model artifacts;
- no external upload;
- no raw examples in model card.

Stop conditions:

- label count below threshold;
- safety violation;
- deterministic baseline still safer.

Review checkpoint:

- decide if prototype remains research-only or proceeds to Phase 5.

## Phase 5 - Embedding/SetFit Prototype

Goal: evaluate whether embeddings improve cue recall without weakening safety.

Inputs:

- stable label schema;
- enough positives per cue;
- local-only reviewed rows;
- synthetic hard negatives.

Outputs:

- aggregate metrics;
- threshold analysis;
- error analysis without row text.

Scripts to build later:

- `scripts/train_local_setfit_prototype.py` only after approval.

Tests:

- no raw text in reports;
- no vector artifacts in git;
- blocked-output suite passes.

Privacy constraints:

- embeddings from private rows stay local-only;
- no provider-hosted embeddings.

Stop conditions:

- evidence selection worsens;
- abstention weakens;
- artifact leak risk increases.

Review checkpoint:

- approve or reject further model complexity.

## Phase 6 - Transformer Fine-Tune Only If Justified

Goal: consider transformer fine-tuning only if data volume and rights justify it.

Inputs:

- 2,000-5,000 reviewed rows or legally approved external training source;
- 200+ positives per important cue;
- frozen holdout;
- source registry approvals.

Outputs:

- local research model;
- detailed model card;
- safety and calibration report.

Scripts to build later:

- only after a separate approved plan.

Tests:

- red-team zero blocked-output violations;
- calibration and abstention tests;
- no raw text or artifacts in git.

Privacy constraints:

- no cloud fine-tuning;
- no CI over private rows;
- no model artifact commits.

Stop conditions:

- source rights unclear;
- labels insufficient;
- output contract cannot be enforced.

Review checkpoint:

- explicit GPT/user and legal/privacy review.

## Phase 7 - Product Integration Behind Feature Flag

Goal: allow a model to assist cue candidate selection without replacing safe rendering.

Inputs:

- approved local model;
- safe output contract;
- renderer enforcement.

Outputs:

- feature flag default off;
- deterministic fallback;
- aggregate monitoring plan.

Scripts:

- none until approved by implementation plan.

Tests:

- feature flag off by default;
- deterministic fallback still works;
- no blocked claims;
- no raw logging.

Privacy constraints:

- model never sees data outside intended runtime path;
- no analytics/tracking added.

Stop conditions:

- model writes final copy;
- unsafe output violation;
- user data persistence introduced.

Review checkpoint:

- product/safety review before beta exposure.

## Phase 8 - Monitoring/Evaluation Loop

Goal: maintain safety and quality without collecting raw content.

Inputs:

- metadata-only feedback;
- aggregate error counts;
- synthetic regression failures;
- local-only reviewer batches.

Outputs:

- safe aggregate dashboard/report;
- active-learning queue by neutral row ID;
- release gate checklist.

Scripts to build later:

- metadata-only report generator.

Tests:

- no raw content in reports;
- no private metadata exposure;
- public copy safety remains green.

Privacy constraints:

- feedback remains metadata-only;
- n8n receives metadata only;
- no raw private content in operations.

Stop conditions:

- raw content needed for workflow;
- legal/privacy gate fails;
- model drift creates unsafe output.

Review checkpoint:

- recurring human review before wider beta or public launch.
