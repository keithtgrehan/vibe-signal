# Agent 3 - NLP Engine Evaluation

## Agent Name
Agent 3 - NLP Engine Evaluation

## Goal
Maintain deterministic cue taxonomy quality with synthetic regression, hard negatives, bootstrap metrics, confusion groups, and human-review packet support.

## Purpose
Evaluate observable wording cues without adding ML, external datasets, or real-world accuracy claims.

## When To Run
Run after cue taxonomy, evidence object, safe-output, regression fixture, or evaluation-report changes.

## Inputs
Synthetic fixtures, cue taxonomy, engine reports, hard-negative cases, reviewed-label scaffolds, and evaluation docs.

## Branch Naming Convention
Use `codex/engine-eval-<short-scope>`.

## Tasks
- Generate bounded synthetic fixtures or full manual 10k suites when requested.
- Run split-aware regression and hard-negative checks.
- Update bootstrap metrics, confusion groups, and false-positive/false-negative reports.
- Prepare human-review packets without claiming human-reviewed accuracy.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`tools/generate_synthetic_whatsapp_fixtures.py`, `tools/analyze_cue_false_positives.py`, `tools/analyze_cue_confusion_groups.py`, `reports/engine_eval/`, `data/synthetic/`, engine tests.

## Files Not To Touch
Web/mobile UI, README polish, production deployment config, raw/private data, external dataset downloads.

## Validation Commands
```bash
bash scripts/engine_eval_all.sh
python -m pytest -q tests/test_api_synthetic_regression_runner.py tests/test_false_positive_analysis.py tests/test_cue_confusion_groups.py
python scripts/check_no_raw_content_leaks.py
```

## Expected Outputs
Synthetic regression reports, bootstrap-only metric summaries, hard-negative findings, and review-packet readiness notes.

## Final Output
Counts, split results, major cue regressions, safety findings, generated reports, and caveats that metrics are bootstrap-only pending human review.

## PR Body Checklist
- Fixture count and split mix
- Eval commands run
- Reports changed
- Safety/claim caveats
- Human-review status

## Failure Conditions
Private data use, external dataset ingestion, ML training, false accuracy claims, or hard-negative unsafe outputs.

## Example Prompt
Run Agent 3 for Vibe Signal. Evaluate the deterministic cue engine with synthetic regression, hard negatives, bootstrap metrics, confusion groups, and false-positive analysis while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
