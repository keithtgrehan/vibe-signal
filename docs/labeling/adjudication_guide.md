# Human Label Adjudication Guide

Status: ready for future human review; no adjudicated labels exist yet.

## Inputs

- Reviewer A labels
- Reviewer B labels, if available
- synthetic review packet
- cue rubric
- validation report from `tools/validate_human_labels.py`

## Disagreement Types

- cue present vs absent
- evidence span does not support cue
- low-signal disagreement
- unsafe wording flag
- reviewer confidence gap

## Adjudication Rules

1. Keep labels about observable wording only.
2. If evidence is weak, mark the cue absent or low-signal.
3. Do not resolve ambiguity by inferring private motives.
4. Do not label cheating, attraction, hidden intent, diagnosis, deception certainty, true emotion, attachment style, or neurotype.
5. Record the reason for each resolved disagreement.

The final adjudicated label file should include reviewer IDs, adjudicator, adjudicated timestamp, and notes. It still does not support production-readiness or broad model-quality claims without a reviewed evaluation plan.

