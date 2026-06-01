# Vibe Matching Evaluation Gates

## Reviewed-Label Thresholds

- `0-49` reviewed labels: synthetic/demo only; no model-quality or benchmark claims.
- `50-99` reviewed labels: internal error analysis allowed; no public benchmark claims.
- `100-499` reviewed labels: limited benchmark reporting allowed; no broad generalization claims.
- `500+` reviewed labels: model-quality claims allowed only with documented metrics, source rights, red-line safety pass, and uncertainty intervals where applicable.

## Always-On Blockers

- Any unsafe output blocks launch.
- Any commercial-unsafe training source in commercial mode blocks launch.
- Any raw private chat committed blocks launch.
- Any raw external dataset committed blocks launch.
- Any provider response committed blocks launch.
- Any vectors, checkpoints, or model binaries committed without explicit approval block launch.

## Current v0 Status

The current baseline uses only synthetic fixtures. Its metrics are harness checks and do not support public model-quality claims.

Run:

```bash
python scripts/validate_vibe_match_pairs.py --input data/vibe_matching/synthetic/synthetic_match_pairs.jsonl
python scripts/train_vibe_matching_baseline.py --input data/vibe_matching/synthetic/synthetic_match_pairs.jsonl --project-mode research_only --report-out reports/vibe_matching/baseline_eval.json --markdown-out reports/vibe_matching/baseline_eval.md
```
