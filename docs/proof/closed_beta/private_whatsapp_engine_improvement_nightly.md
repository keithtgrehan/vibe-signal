# Private WhatsApp Engine Improvement Nightly

## What Was Done Tonight

- Confirmed the raw zip and parsed private JSONL are ignored.
- Confirmed only `data/restricted/private_whatsapp/.gitkeep` and `data/restricted/private_whatsapp/README.md` are tracked under the restricted folder.
- Redacted the local private message JSONL into an ignored restricted redacted JSONL.
- Generated full local review windows and a balanced 100-row review packet.
- Added aggregate stats for private review-window sampling.
- Added aggregate weak-label evaluation for empty-review packets.
- Generated commit-safe synthetic cue fixtures from hand-authored templates inspired by aggregate cue patterns only.
- Added narrow deterministic cue-rule improvements for unclear timing, direct asks, repair wording, cognitive-load delimiters, boundary-pressure precision, and pressure-plus-intensity escalation.
- Added a local-only weak-label baseline experiment with restricted model artifacts.

## What Remains For Human Review

Keith reviews `100` windows in `data/restricted/private_whatsapp/processed/private_label_review_100.csv` tomorrow.

The reviewer should fill `review_label`, `severity`, `safe_next_step`, and `reviewer_notes` using observable wording only. Candidate labels are weak prompts, not ground truth.

## Private Data Handling

- Raw export path: `data/restricted/private_whatsapp/raw/<local-export>.zip`
- Parsed JSONL path: `data/restricted/private_whatsapp/processed/private_messages.jsonl`
- Redacted JSONL path: `data/restricted/private_whatsapp/processed/private_messages_redacted.jsonl`
- Review packet path: `data/restricted/private_whatsapp/processed/private_label_review_100.csv`
- Weak-label report path: `data/restricted/private_whatsapp/processed/private_weak_label_report.md`
- Local model artifact directory: `data/restricted/private_whatsapp/models`

All listed private paths are ignored and must remain out of git.

## Aggregate Ingest Stats

- Parsed private messages: `7278`
- Speaker role counts: `self=4155`, `other=3123`
- Multiline messages: `921`
- Full windows generated locally: `7278`
- First review packet rows: `100`
- First review packet rows needing human review: `100`

## Synthetic Fixture Output

- Synthetic fixture path: `data/synthetic/private_inspired/cue_fixtures.jsonl`
- Synthetic fixture count: `126`
- Summary report: `reports/engine_eval/private_inspired_synthetic_fixture_summary.md`

Synthetic fixtures are hand-authored and do not copy private text, names, dates, or locations.

## Deterministic Rule Changes

- Expanded unclear timing and ambiguity markers such as uncertain timing and tentative wording.
- Expanded direct ask detection for `can we`, `could we`, `should we`, `shall we`, and `are we`.
- Added repair wording patterns for reset and clarification language.
- Added cognitive-load detection for semicolon, slash, and newline-delimited multi-part messages.
- Narrowed `you have to` boundary-pressure behavior so neutral obligation wording does not automatically become boundary pressure.
- Added pressure-plus-intense-punctuation escalation handling without person labels.

## Weak-Label Baseline Status

- Report path: `reports/engine_eval/private_weak_label_model_experiment.md`
- Status: `complete`
- Rows: `100`
- Train rows: `75`
- Test rows: `25`
- Warning: Weak-label local experiment only. Not human-reviewed. Not production. Not a model-quality claim.

The model artifact is restricted and is not loaded by backend runtime.

## Validation Commands

Validation run locally:

- `python -m py_compile tools/redact_private_whatsapp.py tools/prepare_private_label_review.py tools/evaluate_private_cue_labels.py tools/generate_synthetic_from_private_patterns.py tools/train_private_weak_label_baseline.py` passed.
- `python -m pytest tests/test_private_whatsapp_ingestion_safety.py tests/test_private_weak_label_baseline_safety.py -q` passed: `8` tests.
- Relevant engine tests for synthetic cue-rule changes passed: `27` tests.
- `python -m pytest -q` passed.
- `python scripts/check_no_raw_content_leaks.py` passed: `0 finding(s)`.
- `python scripts/check_public_copy_safety.py` passed: `23 finding(s), 23 allowlisted, 0 unallowlisted`.
- `git diff --check` passed.
- Web tests skipped because frontend files were not touched.
- `python scripts/check_vibe_restricted_artifacts.py --staged` passed: `18 path(s) checked`.

## Blocked Claims

No hidden-intent, attraction, deception, diagnosis, neurotype, attachment-style, manipulation, dating-score, relationship-prediction, production-readiness, or accuracy claims are introduced.

## Next Manual Action

Keith reviews 100 windows in private_label_review_100.csv tomorrow.
