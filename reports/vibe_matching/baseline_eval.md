# Vibe Matching Baseline Evaluation

Synthetic-only research baseline. These metrics do not support public model-quality claims.

- Status: `trained`
- Project mode: `research_only`
- Row count: `150`
- Source: `synthetic_vibe_matching`
- Split strategy: `template_category_holdout`
- Benchmark scope: `synthetic_fixture_template_holdout`
- Provider calls made: `False`
- Model artifacts saved: `False`
- Public quality claims supported: `False`

## Metrics

| Label | Accuracy | Precision | Recall | F1 | Trained |
| --- | ---: | ---: | ---: | ---: | --- |
| clarity_fit | 0.600 | 0.000 | 0.000 | 0.000 | true |
| boundary_fit | 1.000 | 0.000 | 0.000 | 0.000 | false |
| repair_fit | 1.000 | 0.000 | 0.000 | 0.000 | false |
| communication_fit | 0.600 | 0.333 | 1.000 | 0.500 | true |
| pressure_risk | 1.000 | 0.000 | 0.000 | 0.000 | false |
| cognitive_load_fit | 0.600 | 0.667 | 0.667 | 0.667 | true |
| inconsistency_cues | 0.800 | 0.000 | 0.000 | 0.000 | true |
| unsupported_claim_shift | 1.000 | 0.000 | 0.000 | 0.000 | false |
| specificity_drop | 0.800 | 0.000 | 0.000 | 0.000 | true |
| answer_evasion_pattern | 0.600 | 0.000 | 0.000 | 0.000 | true |
| contradiction_against_prior_message | 0.800 | 0.000 | 0.000 | 0.000 | false |

## Limits

- Synthetic-only fixtures are useful for harness checks, not real-world quality claims.
- Template-category holdout is still synthetic-only and does not prove generalization.
- Confidence and scores describe analysis quality and observable communication patterns only.
- No deception, attraction, diagnosis, hidden-intent, or relationship-success model is built.
