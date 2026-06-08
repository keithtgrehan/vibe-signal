# Synthetic WhatsApp 10k Pattern Training

This document describes the research-only pattern-recognition baseline built from the existing synthetic WhatsApp fixture corpus.

## Purpose

The baseline is a local sklearn cue-family proposer trained only on synthetic WhatsApp-style fixtures. It is intended for development scaffolding, error analysis, and regression discipline around observable wording-pattern cues.

It does not replace the deterministic evidence-first engine.

## Source Corpus

Discovered source path:

- `data/synthetic/whatsapp/conversations.jsonl`
- `data/synthetic/whatsapp/fixture_manifest.json`
- split copies under `data/synthetic/whatsapp/dev/`, `hard_negative/`, `heldout/`, and `red_team/`

The source manifest reports:

- `10000` synthetic messages
- `5000` synthetic conversations
- source type: `synthetic_fixture`
- no real chats, tester data, external datasets, or provider outputs

The training-row builder writes one row per synthetic conversation, preserving the message array and flattening the synthetic conversation into `text_for_training`.

## Why This Source Is Allowed

The source tier is:

`bronze_synthetic_whatsapp_10k`

Rows are marked:

- `source_type: synthetic_fixture`
- `rights_review_status: synthetic_only`
- `consent_status: not_required_synthetic`
- `contains_raw_private_text: false`
- `contains_personal_data: false`
- `commercial_training_allowed: false`
- `research_training_allowed: true`
- `production_use_allowed: false`
- `model_quality_claims_allowed: false`

This permits research-only baseline training but does not permit commercial training, production use, or public model-quality claims.

## Allowed Cue Families

- `directness`
- `specificity`
- `specificity_drop`
- `ambiguity`
- `unclear_ask`
- `hedging`
- `reassurance`
- `alignment`
- `pressure`
- `urgency`
- `boundary_pressure`
- `consent_clarity`
- `conflict`
- `escalation_risk`
- `repair_opportunity`
- `topic_shift`
- `answer_evasion_pattern`
- `cognitive_load`
- `overloaded_message`
- `contradiction_against_prior_message`
- `unsupported_claim_shift`
- `low_signal`
- `neutral`

Unsupported fixture cues that are not in the training target, such as `response_timing`, are excluded from model labels and reported in the manifest.

## Blocked Claims And Labels

The row builder, validator, and trainer block labels or outputs for:

- attraction
- hidden intent
- deception certainty
- emotional truth
- cheating
- diagnosis
- therapy need
- neurotype
- attachment style
- manipulation claims
- abuse certainty
- relationship outcomes
- gaslighting
- compatibility prediction

The generated rows also include forbidden-output expectations such as:

- `they like you`
- `they are lying`
- `this proves`
- `hidden intent`
- `gaslighting`
- `manipulating you`
- `diagnosis`
- `attachment style`
- `narcissist`
- `abusive person`
- `make them respond`
- `win them back`

These are blocked strings, not product capabilities.

## Training Row Schema

Each row contains:

- stable `row_id`
- source tier and synthetic rights metadata
- split and scenario metadata
- synthetic message array with canonical speaker roles
- `text_for_training`
- allowed `expected_cues`
- cue-level evidence spans
- blocked interpretations
- forbidden-output expectations
- neutral `safe_summary`
- neutral `safe_next_step`

Rows missing synthetic provenance, rights flags, expected-cue safety, evidence coverage, or safe-output boundaries fail validation.

## Convert Fixtures

```bash
python tools/build_pattern_training_rows_from_synthetic_whatsapp.py \
  --input-dir data/synthetic/whatsapp \
  --out data/training/pattern_recognition/synthetic_whatsapp_10k_training_rows.jsonl \
  --manifest-out data/training/pattern_recognition/synthetic_whatsapp_10k_manifest.json \
  --report-out reports/pattern_training/synthetic_whatsapp_10k_training_rows_report.md
```

## Validate Rows

```bash
python tools/validate_synthetic_whatsapp_training_rows.py \
  --input data/training/pattern_recognition/synthetic_whatsapp_10k_training_rows.jsonl \
  --manifest data/training/pattern_recognition/synthetic_whatsapp_10k_manifest.json
```

## Train Research Baseline

```bash
python scripts/train_synthetic_whatsapp_pattern_baseline.py \
  --input data/training/pattern_recognition/synthetic_whatsapp_10k_training_rows.jsonl \
  --project-mode research_only \
  --report-out reports/pattern_training/synthetic_whatsapp_10k_baseline_report.json \
  --markdown-out reports/pattern_training/synthetic_whatsapp_10k_baseline_report.md
```

Optional local artifact command:

```bash
python scripts/train_synthetic_whatsapp_pattern_baseline.py \
  --input data/training/pattern_recognition/synthetic_whatsapp_10k_training_rows.jsonl \
  --project-mode research_only \
  --report-out reports/pattern_training/synthetic_whatsapp_10k_baseline_report.json \
  --markdown-out reports/pattern_training/synthetic_whatsapp_10k_baseline_report.md \
  --local-artifact-out .local_artifacts/pattern_baseline/synthetic_whatsapp_10k_model.joblib
```

## Artifact Policy

By default the trainer writes reports only and does not save a model artifact.

If `--local-artifact-out` is used, the path must be under `.local_artifacts/`. The repo ignores local model/vector formats including `.joblib`, `.pkl`, `.onnx`, `.pt`, `.safetensors`, `.bin`, `.vec`, `.faiss`, and `.index`.

Do not commit model artifacts, vectors, embeddings, checkpoints, or training outputs beyond the JSON/Markdown reports.

## Deterministic Engine Primary

The deterministic cue engine remains primary. The sklearn baseline is a research-only cue-family proposer.

Model output must not be rendered directly in product UI. Any future model-assisted cue output would need:

- evidence-span validation
- safe-output blocker
- blocked-claim sanitizer
- low-signal fallback
- human-reviewed evaluation gate

## What This Does Not Prove

Synthetic-only metrics are development signals only. They are not real-world validation, model-quality proof, production-readiness proof, legal/compliance approval, or a claim that Vibe Signal can infer hidden intent, attraction, deception, diagnosis, manipulation, abuse, or relationship outcomes.

The next step before any product promotion is human-reviewed labels and error analysis under the same safety boundaries.
