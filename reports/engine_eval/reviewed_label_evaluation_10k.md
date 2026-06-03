# Reviewed Label Evaluation

Status: `bootstrap-only`.

These metrics compare engine/API observed cue IDs against synthetic bootstrap or future human-reviewed cue labels. They are not real-world accuracy or model-quality proof.

- Label status: `bootstrap`
- Label rows: `105000`
- API result rows: `5000`
- Micro precision: `0.5732`
- Micro recall: `0.6827`
- Micro F1: `0.6232`
- Macro precision: `0.6494`
- Macro recall: `0.5483`
- Macro F1: `0.7223`
- TP/FP/FN/TN: `4911/3657/2283/94149`

## Split Metrics

- `dev`: precision `0.5595`, recall `0.7015`, F1 `0.6225`, FP `2923`, FN `1580`
- `hard_negative`: precision `0.6416`, recall `0.4979`, F1 `0.5607`, FP `334`, FN `603`
- `heldout`: precision `0.6`, recall `0.8571`, F1 `0.7059`, FP `400`, FN `100`
- `red_team`: precision `None`, recall `None`, F1 `None`, FP `0`, FN `0`

Human-reviewed labels are required before any validation or quality claim.
