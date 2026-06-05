# Local Gold Evaluator Scaffold

Date: 2026-06-06

Status: phase_1_scaffold_requires_gpt_user_review. This is not legal advice, not model approval, and not approval to train.

## Purpose

This scaffold validates and evaluates local-only private gold-review label files in aggregate. It is designed for schema QA, evaluator smoke tests, weak-label calibration planning, and active-learning design.

It does not train a model, create model artifacts, use public datasets, download datasets, or produce production-readiness claims.

## Why 30 Rows Is Not Enough For Training

Approximately 30 reviewed rows can show whether the schema is usable and whether the evaluator can read labels safely. That volume is not enough for model training, model selection, or production claims.

At this stage, 30 rows means schema/evaluator smoke only. Training remains blocked until enough reviewed rows exist per broad cue family and until separate support exists for any leaf cue that might become a model target.

## Local-Only Privacy Rules

- Inputs must live under the restricted local root: `data/restricted/private_whatsapp/**`.
- Use the processed subdirectory under that root for local review files.
- Use the reports subdirectory under that root for generated evaluator summaries.
- Console output is aggregate-only.
- Reports are aggregate-only.
- Row text, message text, evidence text, reviewer notes, source identifiers, filenames, and row-level examples must not be printed or committed.
- Generated reports remain ignored local artifacts.
- n8n workflows must not receive raw private content, private labels, or source-identifying metadata.

## Validator

Use a local path placeholder rather than committing or pasting a real filename:

```bash
export VIBE_PRIVATE_ROOT="data/restricted/private_whatsapp"
python tools/validate_private_gold_labels.py \
  --input "$VIBE_PRIVATE_ROOT/processed/<local-review-file>.csv"
```

The validator checks:

- one row ID column is present;
- one gold label column is present;
- missing required values are counted;
- invalid labels are counted;
- rejected and low-signal rows are counted;
- severity, cue, and safe-next-step distributions are aggregated;
- unknown columns are counted without printing cell values.

CSV is the required format. XLSX is supported only when `openpyxl` is already available in the local environment; no dependency is added for this scaffold.

## Evaluator

Use a local path placeholder and keep output under the restricted local root:

```bash
export VIBE_PRIVATE_ROOT="data/restricted/private_whatsapp"
python tools/evaluate_private_gold_labels.py \
  --input "$VIBE_PRIVATE_ROOT/processed/<local-review-file>.csv" \
  --output "$VIBE_PRIVATE_ROOT/reports/private_gold_eval_summary.md"
```

If prediction columns are absent, the evaluator runs in schema/label QA only mode.

If prediction columns are present, it reports aggregate:

- per-label precision, recall, and F1;
- confusion counts;
- disagreement count;
- missing evidence-span count.

Low-signal and rejected rows are counted separately and are not treated as normal cue-disagreement examples.

## Thresholds Before Training

Training remains blocked until a future reviewed plan approves it. Planning thresholds from the research plan are:

- 50-100 reviewed rows: schema sanity and evaluator smoke.
- 250-400 reviewed rows: weak-label calibration and confusion analysis.
- 600-1,000 reviewed rows: first local classical baseline at broad cue-family level only.
- 80-100 positive examples per primary cue family before any local baseline.
- Separate reviewed positive and hard-negative support before any leaf-cue model.
- Legal, privacy, source-rights, and safety gates must pass before any product-affecting model work.

## Next Step After More Labels

After more local labels exist, the next step is to review aggregate evaluator output, tune the label schema, and identify active-learning queues by neutral row ID only. Do not move to training until the Phase 1 review explicitly approves a training plan.

## Explicit Non-Goals

- No model trained.
- No model artifact generated.
- No public dataset used.
- No public dataset downloaded.
- No provider upload.
- No CI run over private rows.
- No row-level private examples in docs, tests, pull requests, reports, screenshots, or issue text.

