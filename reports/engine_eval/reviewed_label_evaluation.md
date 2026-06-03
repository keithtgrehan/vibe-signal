# Reviewed Label Evaluation

Status: `bootstrap-only`.

These metrics compare engine/API observed cue IDs against synthetic bootstrap or future human-reviewed cue labels. They are not real-world accuracy or model-quality proof.

- Label status: `bootstrap`
- Label rows: `105000`
- API result rows: `5000`
- Micro precision: `0.6646`
- Micro recall: `0.947`
- Micro F1: `0.7811`
- Macro precision: `0.7998`
- Macro recall: `0.9379`
- Macro F1: `0.8278`
- TP/FP/FN/TN: `7055/3560/395/93990`

## Split Metrics

- `dev`: precision `0.604`, recall `0.9242`, F1 `0.7306`, FP `3160`, FN `395`
- `hard_negative`: precision `1.0`, recall `1.0`, F1 `1.0`, FP `0`, FN `0`
- `heldout`: precision `0.6364`, recall `1.0`, F1 `0.7778`, FP `400`, FN `0`
- `red_team`: precision `None`, recall `None`, F1 `None`, FP `0`, FN `0`

Human-reviewed labels are required before any validation or quality claim.
