# Cue Improvement Backlog

This backlog is generated from synthetic API regression findings. It is not an accuracy claim, model-quality proof, validation, or production-readiness evidence.

## Highest Priority

- Split `answer_evasion_pattern` from ordinary topic-shift co-firing. Current bootstrap precision is `0.4129` with `337` false positives and `79` false negatives.
- Reduce `hedging` co-firing in ambiguity templates. Current bootstrap precision is `0.3125`.
- Tighten `escalation_risk` so it does not over-count pressure/conflict combinations that are already represented by more specific cues. Current bootstrap precision is `0.3192`.
- Continue narrowing `specificity` and `directness` in dev examples without weakening hard-negative precision.

## Remaining False Negatives

- `contradiction_against_prior_message`: `158` bootstrap false negatives remain, primarily from private-eval two-message constraints where expected metadata asks for more multi-message cues than the fixture can support.
- `alignment`: `79` bootstrap false negatives remain in direct-answer fixtures.
- `ambiguity`: `79` bootstrap false negatives remain in indirect-ask fixtures.
- `answer_evasion_pattern`: `79` bootstrap false negatives remain.

## Next Fixture Types

- Topic bridge that explicitly promises an answer and later answers.
- Concrete direct answer without alignment wording.
- Deadline-bearing request without urgency semantics.
- Vague timing without hedging.
- Private-eval multi-turn conversation that can support contradiction, specificity drop, and evasion labels without adding unsafe product claims.

## Guardrails

- Do not tune on real/private chats.
- Do not add external datasets.
- Do not claim accuracy from bootstrap labels.
- Keep private evaluation labels out of product output.
