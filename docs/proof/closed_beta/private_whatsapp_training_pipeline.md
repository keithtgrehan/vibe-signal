# Private WhatsApp Training Pipeline Proof

## What Was Built

- `.gitignore` rules for restricted private WhatsApp exports, zips, parsed rows, redacted rows, and private review CSVs.
- A local restricted folder at `data/restricted/private_whatsapp/` with safety instructions.
- A private source example config that blocks commercial and product training.
- Local CLI tools for ingesting a WhatsApp zip, redacting parsed rows, preparing cue-label review CSVs, and evaluating reviewed labels in aggregate.
- Synthetic-only tests for parser behavior, multiline messages, restricted output enforcement, no raw stdout leakage, git ignore coverage, and review CSV columns.

## What Was Not Built

- No raw private chat data was added.
- No parsed private messages were added.
- No participant names were added.
- No model was trained.
- No backend runtime behavior changed.
- No frontend behavior changed.
- No production claim was added.

## Raw Data Status

Raw WhatsApp exports and derived private files must remain outside git or under `data/restricted/private_whatsapp/`, which is ignored except for `.gitkeep` and `README.md`.

## Future Training Gate

Future cue-model training requires human-reviewed labels, consent documentation, deletion handling, source-rights review, and a separate approval. Weak candidate labels from the preparation tool are review prompts only.

## Allowed Cue Labels

- `ambiguity`
- `unclear_timing`
- `direct_ask`
- `unanswered_ask_candidate`
- `pressure_urgency`
- `boundary`
- `reassurance`
- `repair_attempt`
- `escalation_risk`

## Blocked Claims

The pipeline must not produce claims about hidden intent, attraction, deception, cheating, diagnosis, neurotype, attachment style, emotional truth, manipulation, dating scores, relationship prediction, or outcome prediction.

## Validation Results

Validation run locally:

- `python -m py_compile tools/ingest_private_whatsapp.py tools/redact_private_whatsapp.py tools/prepare_private_label_review.py tools/evaluate_private_cue_labels.py` passed.
- `python -m pytest tests/test_private_whatsapp_ingestion_safety.py -q` passed: `6 passed`.
- `git diff --check` passed.
- `python scripts/check_no_raw_content_leaks.py` passed: `0 finding(s)`.
- `python scripts/check_public_copy_safety.py` passed: `23 finding(s), 23 allowlisted, 0 unallowlisted`.
- `python scripts/check_vibe_restricted_artifacts.py --staged` passed: `12 path(s) checked`.
