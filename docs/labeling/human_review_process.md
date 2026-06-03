# Human Review Process

Status: human-reviewed labels are pending.

The current 10k evaluation uses synthetic bootstrap labels. Bootstrap labels are useful for regression and contract checks, but they are not human-reviewed validation and must not be described as accuracy.

## Workflow

1. Generate or refresh the review packet:

   ```bash
   python tools/create_human_review_packet.py --v2
   ```

2. Prepare blank label templates:

   ```bash
   python tools/prepare_human_label_review.py
   ```

3. Reviewer A labels observable wording only in `data/review/human_label_template.csv` or a copied review file.
4. Optional Reviewer B independently labels the same packet.
5. Validate each label file:

   ```bash
   python tools/validate_human_labels.py --labels data/review/human_reviewed_labels.jsonl
   ```

6. Resolve disagreements into an adjudicated file.
7. Evaluate only after real human labels exist:

   ```bash
   python tools/evaluate_human_reviewed_labels.py --labels data/review/human_reviewed_labels.jsonl
   ```

## Reviewer Boundaries

Reviewers label observable wording only. Reviewers must not label:

- hidden intent
- cheating
- attraction
- diagnosis
- deception certainty
- true emotion
- attachment style
- neurotype

## Label Statuses

- `bootstrap`: derived from synthetic fixture expectations; not human-reviewed.
- `human-reviewed`: completed by a named human reviewer; still not a real-world accuracy claim by itself.
- `adjudicated`: disagreement-resolved label set reviewed by an owner.

Human-reviewed labels are required before any validation or model-quality claim.

