# Agent 5 - Evaluation And Benchmark Plan

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. No private rows are included.

## Evaluation Before Training

Build the evaluator before any training script. The evaluator should run locally over ignored private files only when explicitly invoked, and it should produce aggregate metrics or redacted reports.

## Split Strategy

Private local gold:

- `local_gold_smoke`: 30-100 rows for schema and evaluator smoke, not model selection.
- `local_gold_dev`: later reviewed rows for threshold tuning.
- `local_gold_holdout`: frozen and never used for training or active-learning selection.

Synthetic:

- checked into repo;
- used in CI;
- covers expected cue behavior and hard negatives;
- cannot support real-world accuracy claims.

Public benchmarks:

- metadata-only until approved;
- benchmark use only after a registry row approves the specific evaluation purpose;
- never merged into private gold;
- never used to claim product accuracy without legal/harm review and fit analysis.

## Metrics

Cue-level:

- precision;
- recall;
- F1;
- support count;
- confusion matrix by cue;
- false-positive rate on hard negatives.

Evidence:

- exact span match for synthetic;
- overlap score for local-only private eval;
- missing-evidence rate;
- evidence-to-label consistency.

Safety:

- blocked-output violation rate;
- cannot-infer statement presence;
- no coercive reply suggestions;
- no diagnosis/therapy framing;
- no hidden-intent or attraction claims;
- no raw text in logs/reports.

Abstention:

- low-signal recall;
- abstention precision;
- unsafe-overconfident rate;
- threshold coverage by cue.

Calibration:

- reliability bins;
- expected calibration error later;
- per-cue threshold curves;
- confidence vs reviewer confidence.

## Baselines To Compare

1. deterministic engine only;
2. deterministic plus weak supervision labels;
3. classical TF-IDF plus deterministic features;
4. embedding nearest-neighbor prototype;
5. SetFit prototype;
6. transformer fine-tune only if justified.

The production baseline remains deterministic until a model beats it on local aggregate metrics and safety gates.

## Report Format

Future local report should include:

- source registry version;
- label schema version;
- local run timestamp;
- row counts only;
- cue support counts;
- aggregate metrics;
- confusion matrix;
- hard-negative failure summary;
- low-signal performance;
- safety violation count;
- abstention threshold table;
- next active-learning queues by neutral row ID only.

No report should include raw private message text, private source identifiers, private filenames, screenshots, or row-level examples from private data.

## Pass/Fail Gates Before Model Affects Product

Required:

- zero blocked-output violations on red-team suite;
- no raw private content in generated reports;
- evidence present for every non-low-signal result;
- model abstains when evidence is weak;
- model does not produce user-facing copy directly;
- deterministic baseline comparison is documented;
- legal/source registry approvals exist;
- product output renderer enforces safe contract.

Suggested thresholds for first internal feature flag:

- at least 600 reviewed rows for broad cue-family prediction only;
- at least 80 positives per enabled cue family;
- leaf sub-cues disabled unless each leaf has its own reviewed positive and hard-negative support;
- precision target higher than recall for sensitive cues;
- false-positive rate on hard negatives below agreed threshold;
- low-signal recall high enough to prevent over-interpretation;
- no regression in public copy and no-raw-content tests.

## Scripts To Build Later

Do not build in this research sprint. Later scripts can be:

- `scripts/eval_local_gold.py`: local-only aggregate evaluator.
- `scripts/build_synthetic_vibe_fixtures.py`: generated synthetic fixtures with human review.
- `scripts/compare_weak_labels.py`: deterministic/weak/human comparison.
- `scripts/report_model_card_metrics.py`: redacted model card metrics.
- `scripts/select_active_learning_rows.py`: neutral row-ID sampling only.

Each future script must default to no private path and require explicit local ignored input.
