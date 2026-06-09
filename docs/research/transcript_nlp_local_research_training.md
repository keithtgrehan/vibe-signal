# Transcript NLP Local Research Training

This document describes the local research-only transcript NLP scaffold built on top of the synthetic WhatsApp pattern-training pipeline from PR #72.

## Purpose

The goal is to benchmark a local cue-family proposer using:

- synthetic WhatsApp training rows already committed in the repo;
- optional local GoEmotions rows after Apache-2.0 metadata confirmation;
- optional local MELD text CSV rows under GPL-3.0, local-only, non-commercial constraints.

This is research scaffolding only. It does not change the production app, backend, frontend, mobile app, deterministic cue engine, API contracts, or safety gates.

## Source Boundaries

Synthetic WhatsApp rows:

- path: `data/training/pattern_recognition/synthetic_whatsapp_10k_training_rows.jsonl`
- source tier: `bronze_synthetic_whatsapp_10k`
- committed because rows are synthetic fixtures
- deterministic engine remains primary

GoEmotions:

- dataset: `google-research-datasets/go_emotions`
- source: `https://huggingface.co/datasets/google-research-datasets/go_emotions`
- required license metadata: `apache-2.0`
- config/splits: simplified train/validation/test
- local source tier: `goemotions_local_research_apache2`
- rows may be cached only under ignored `data/external/goemotions/`
- raw rows must not be committed

MELD:

- dataset: `declare-lab/MELD`
- source: `https://huggingface.co/datasets/declare-lab/MELD`
- project: `https://github.com/declare-lab/MELD`
- required license metadata: `gpl-3.0`
- local source tier: `meld_local_research_gpl3_nc`
- local text CSV only
- no audio/video use
- non-commercial research only
- raw transcript rows must not be committed

EmpatheticDialogues remains registered only and blocked until license terms are explicitly recorded.

## Cue Mapping Rule

External emotion or sentiment labels are weak signals only. They are never treated as emotion truth, hidden intent, attraction, deception, diagnosis, manipulation, abuse, compatibility, or relationship-outcome evidence.

The builders emit an expected Vibe cue only when observable text supports it with an evidence span.

Allowed cue families are the same observable communication-pattern labels used by the synthetic WhatsApp baseline, including directness, ambiguity, reassurance, alignment, pressure, conflict, repair opportunity, topic shift, low signal, and neutral.

## Commands

Prepare GoEmotions locally:

```bash
python tools/prepare_goemotions_local_research_cache.py \
  --cache-out data/external/goemotions/simplified \
  --manifest-out data/external/goemotions/goemotions_local_manifest.json
```

Validate local MELD CSVs:

```bash
python tools/validate_meld_local_research_source.py \
  --input-dir data/external/meld/MELD.Raw/data/MELD \
  --manifest-out data/external/meld/meld_local_manifest.json
```

Build local weak-label rows:

```bash
python tools/build_goemotions_local_research_rows.py \
  --manifest data/external/goemotions/goemotions_local_manifest.json \
  --out data/external/goemotions/goemotions_vibe_rows.jsonl \
  --report-out reports/pattern_training/goemotions_local_augmentation_report.md

python tools/build_meld_local_research_rows.py \
  --manifest data/external/meld/meld_local_manifest.json \
  --out data/external/meld/meld_vibe_rows.jsonl \
  --report-out reports/pattern_training/meld_local_augmentation_report.md
```

Validate combined rows:

```bash
python tools/validate_transcript_nlp_local_research_rows.py \
  --synthetic-input data/training/pattern_recognition/synthetic_whatsapp_10k_training_rows.jsonl \
  --augmentation-input goemotions:data/external/goemotions/goemotions_vibe_rows.jsonl \
  --augmentation-input meld:data/external/meld/meld_vibe_rows.jsonl
```

Train local research baseline:

```bash
python scripts/train_transcript_nlp_local_research_baseline.py \
  --synthetic-input data/training/pattern_recognition/synthetic_whatsapp_10k_training_rows.jsonl \
  --augmentation-input goemotions:data/external/goemotions/goemotions_vibe_rows.jsonl \
  --augmentation-input meld:data/external/meld/meld_vibe_rows.jsonl \
  --project-mode research_only \
  --report-out reports/pattern_training/transcript_nlp_local_research_report.json \
  --markdown-out reports/pattern_training/transcript_nlp_local_research_report.md
```

If local external caches are unavailable, omit `--augmentation-input`. The trainer will run on synthetic rows only and report that GoEmotions/MELD were not included.

## Artifact Policy

The trainer writes reports only by default. Optional model artifacts must be written under `.local_artifacts/`.

Do not commit:

- GoEmotions rows
- MELD rows
- Reddit comments
- TV-show transcript snippets
- audio/video
- model artifacts
- vectors
- embeddings
- checkpoints
- local cache manifests containing raw-row paths if they expose private local state

## Non-Claims

Synthetic and local public-dataset metrics are development signals only. They are not real-world validation, model-quality proof, production-readiness proof, legal/compliance approval, or a claim that Vibe Signal can infer hidden intent, attraction, deception, diagnosis, manipulation, abuse, or relationship outcomes.

The deterministic cue engine remains primary. Future model-assisted output would need evidence-span validation, safe-output blocking, blocked-claim sanitization, low-signal fallback, and a human-reviewed evaluation gate before any product promotion.
