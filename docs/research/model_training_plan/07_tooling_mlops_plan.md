# Agent 7 - Tooling And MLOps Plan

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. No dependencies or training scripts are added by this plan.

## Recommended Tool Stack

Already available or appropriate for the first future implementation:

- Python standard library for registry validation and redacted reports.
- pytest for eval gates and safety checks.
- pandas or polars later for local-only workbook/report processing.
- scikit-learn for TF-IDF and classical baselines.
- joblib or skops later for local-only prototype persistence.

Later:

- sentence-transformers for local embedding experiments.
- SetFit for few-shot prototypes.
- Hugging Face transformers only after label volume and rights gates pass.
- Snorkel or a lightweight local weak-supervision layer for labeling-function analysis.
- ONNX only after a model is approved for deployment study.

Avoid now:

- DVC unless there is a clear local-only artifact workflow and no remote data risk;
- MLflow server unless local-only and no raw text logging is enforced;
- cloud training;
- provider-hosted fine-tuning;
- external experiment trackers;
- automatic artifact upload.

## Local Folder Structure For Future Work

Future local-only paths should stay ignored and outside public surfaces:

- restricted private data root: `data/restricted/private_whatsapp/**`;
- local model artifacts: ignored restricted model area, not documented with private filenames;
- local evaluation reports: ignored restricted report area, aggregate/redacted only;
- local vector indexes: ignored restricted artifact area.

Tracked repo paths may contain:

- schemas;
- scripts that do not read private paths by default;
- synthetic fixtures;
- aggregate redacted report templates;
- model cards without artifacts;
- dataset registry metadata.

## Scripts To Build Later

Do not build these now. Future scripts should be reviewed before implementation:

- `scripts/validate_training_source_registry.py`: fail-closed registry validation.
- `scripts/eval_local_gold.py`: aggregate-only local evaluator.
- `scripts/generate_synthetic_fixture_pack.py`: no private examples in prompts.
- `scripts/compare_weak_supervision.py`: labeling function coverage/conflict.
- `scripts/train_local_classical_baseline.py`: disabled until label thresholds are met.
- `scripts/export_redacted_model_report.py`: no raw rows or private IDs.

Every script must:

- refuse to run on non-ignored private input unless explicitly approved;
- avoid raw text logging;
- avoid network calls by default;
- write only aggregate or redacted outputs unless local-only and ignored;
- fail if output path is tracked or public.

## CI Guardrails

CI should run:

- private metadata exposure check;
- public copy safety check;
- no-raw-content leak check;
- restricted artifact check;
- synthetic engine tests;
- web build and tests.

CI should not:

- download external datasets;
- read ignored private data;
- upload private artifacts;
- publish model checkpoints;
- call n8n with raw content;
- run provider training jobs.

## Artifact Rules

Allowed in git:

- docs;
- schemas;
- registry examples with neutral IDs;
- synthetic fixtures;
- tests;
- redacted aggregate templates.

Blocked in git:

- raw private data;
- private metadata;
- private workbooks;
- private processed corpora;
- vectors/embeddings from private rows;
- model checkpoints;
- local eval reports with row text;
- screenshots containing private content.

## Persistence Notes

Relevant source:

- scikit-learn model persistence cautions and skops mention: https://scikit-learn.org/stable/model_persistence.html
- skops secure persistence docs: https://skops.readthedocs.io/

Recommendation:

- use no persisted model artifact until a model passes gates;
- when persistence is needed, keep local-only, ignored, and include provenance metadata;
- never load untrusted pickle artifacts.
