# Vibe Matching v0 Model Card

## Intended Use

Vibe Matching v0 compares observable communication patterns in short exchanges. It reports compatibility and friction signals such as directness, specificity, low-pressure wording, repair readiness, consent clarity, boundary respect, answer evasiveness cues, specificity drops, unsupported claim shifts, and deterministic contradiction cues.

## Not Intended Use

This system must not be used for deception detection, hidden-intent prediction, attraction prediction, cheating detection, diagnosis, neurotype inference, attachment-style scoring, emotional-truth claims, manipulation claims, or response optimization designed to make someone respond.

## Training Data

The research-only sklearn baseline uses `data/vibe_matching/synthetic/synthetic_match_pairs.jsonl`. The fixture rows are synthetic, hand-authored, and not copied from private chats, external datasets, or provider responses.

External datasets remain metadata-only, manual-review, or blocked until rights, consent, privacy, provenance, and harm review are complete.

## Metrics

Metrics in `reports/vibe_matching/baseline_eval.json` and `reports/vibe_matching/baseline_eval.md` are synthetic-only harness checks. The current generated report shows perfect fixture metrics because the synthetic templates are intentionally simple and repeated; this is not real-world model quality. These metrics do not support public benchmark or model-quality claims.

## Confidence Meaning

Confidence means confidence in the analysis quality and evidence strength. It does not mean confidence about another person's truthfulness, motive, attraction, emotional state, or diagnosis.

## Failure Modes

- Short or one-sided exchanges can produce low-confidence analysis.
- Vague replies can reduce analysis stability.
- Deterministic contradiction cues are pattern-level and may miss context.
- Synthetic-only baselines can overfit fixture wording and should not be treated as real-world performance.

## Launch Claim Limits

Allowed: observable communication-pattern comparison, compatibility and friction signals, specificity consistency, answer-evasiveness cues, contradiction cues, and analysis uncertainty.

Blocked: deception, hidden intent, attraction, cheating, diagnosis, neurotype, attachment style, manipulation, emotional truth, relationship-success prediction, and response optimization claims.

## Reviewed-Label Threshold

Before real model-quality claims, the project needs at least `500+` consented reviewed labels, documented metrics, uncertainty intervals where applicable, source-rights approval, and a red-line safety pass.
