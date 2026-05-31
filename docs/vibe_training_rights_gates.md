# Vibe Training Source Rights Gates

## Purpose

This registry and validator keep Vibe training-source research in a metadata-only state. They document candidate source rights, allowed project modes, and blocked use before any external source can be treated as training-ready.

This work does not add dataset downloads, raw rows, corpus generation, model training, vector generation, provider fetching, or production ML readiness.

## Project Modes

| Mode | Meaning |
| --- | --- |
| `research_only` | Allows only explicitly marked research-only training rows and non-training reference rows. NC rows pass only when `research_only: true`, `training_use_allowed: true`, and `usage: research_only`. |
| `commercial` | Fails closed unless every row is training-allowed, commercial-allowed, not research-only, and not in a blocked rights tier. The example registry intentionally fails in this mode. |

## Allowed Use

- Metadata-only registry review.
- Research-only rights gating for explicitly marked NC rows.
- Reference-only tracking for manual-review, restricted, and eval-only sources.
- Dry-run manifests that confirm no download, corpus, model, vector, provider, or training artifact is produced.

## Blocked Use

- Dataset download or scraping.
- Committing raw rows, transcripts, audio, video, screenshots, or sensitive reports.
- Creating corpus JSONL rows from external sources.
- Training, fine-tuning, embeddings, vector indexes, or model artifacts.
- Provider/API fetching.
- Commercial use of NC, research-only, manual-review, restricted, eval-only, or unknown-rights rows.
- Treating source labels as internal user truth, diagnosis, attraction, protected-trait, deception, or hidden-intent evidence.

## Dataset Rights Posture

| Source | Rights posture | Training posture | Commercial posture |
| --- | --- | --- | --- |
| GoEmotions | Manual review/reference-only until dataset-specific rights are documented. | Blocked. | Blocked. |
| Civil Comments | Manual review/reference-only until source and competition terms are verified. | Blocked. | Blocked. |
| DailyDialog | NC research-only. | Allowed only for research-only mode. | Blocked. |
| EmpatheticDialogues | NC research-only. | Allowed only for research-only mode. | Blocked. |
| MELD | Eval-only/reference due media-rights constraints. | Blocked. | Blocked. |
| CMU-MOSEI / MOSI | Restricted/manual-review. | Blocked. | Blocked. |
| MSP-Podcast | Restricted/manual-review. | Blocked. | Blocked. |
| IEMOCAP | Restricted/manual-review. | Blocked. | Blocked. |
| Consent/coercion/safety placeholders | Manual-review placeholders only. | Blocked. | Blocked. |
| Neurodivergent communication placeholders | Manual-review or restricted placeholders only. | Blocked. | Blocked. |

## Validator Commands

```bash
python scripts/validate_vibe_training_sources.py \
  --config configs/vibe_training_sources.example.yml \
  --project-mode research_only
```

```bash
python scripts/validate_vibe_training_sources.py \
  --config configs/vibe_training_sources.example.yml \
  --project-mode commercial
```

Expected result: `research_only` passes the example registry; `commercial` fails closed because the example includes NC, manual-review, restricted, and eval-only rows.

## Dry-Run Command Examples

```bash
python scripts/download_research_datasets.py \
  --all-approved-research \
  --project-mode research_only \
  --dry-run \
  --manifest-out /tmp/vibe_download_manifest.json
```

```bash
python scripts/build_vibe_training_corpus.py \
  --project-mode research_only \
  --dry-run \
  --output /tmp/vibe_corpus.jsonl \
  --manifest-out /tmp/vibe_corpus_manifest.json
```

```bash
python scripts/train_research_vibe_baseline.py \
  --project-mode research_only \
  --dry-run \
  --report-out /tmp/vibe_trainer_dry_run.json
```

## Acceptance Criteria

- Missing required fields fail validation.
- Unknown or ambiguous rights fail validation.
- Manual-review, restricted, and eval-only rows never pass as training-ready.
- Commercial mode rejects NC, research-only, manual-review, restricted, eval-only, unknown, non-training, and non-commercial rows.
- Research-only mode allows NC training only when the row explicitly declares research-only use.
- Dry-run scripts never download, create corpus rows, train, create vectors, call providers, or write model artifacts.
- Restricted artifact scans block raw data, transcripts, audio/video, model artifacts, vector artifacts, provider artifacts, and training outputs.

## Intentionally Not Implemented

- Real external source download.
- Raw data storage.
- Corpus row creation from external sources.
- Training or fine-tuning.
- Embeddings or vector indexes.
- Provider/API access.
- Production ML readiness claims.
