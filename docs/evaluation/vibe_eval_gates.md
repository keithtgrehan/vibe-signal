# Vibe Evaluation Gates

This scaffold evaluates reviewed-label and evidence readiness without adding model training, embedding benchmarks, provider benchmarks, or production-quality claims.

Metrics:

- `reviewed_label_count`
- `matched_labels`
- `unmatched_labels`
- `potential_false_positives`
- `missing_evidence`
- `unsupported_claim_count`
- `blocked_output_count`

Gate rules:

- Below 50 reviewed labels: no ML or benchmark claims.
- Below 100 reviewed labels: no retrieval-quality claims.
- Below 500 reviewed labels: no model-quality claims.
- Any unsafe output claim fails.
- Provider outputs cannot be canonical.
- Evidence objects cannot override deterministic outputs.
- Statistical-significance language is not allowed.

Run:

```bash
python scripts/evaluate_vibe_outputs.py --gold-labels data/vibe_gold/example_gold_labels.jsonl --evidence tests/fixtures/evidence_objects/valid_evidence_objects.jsonl
```
