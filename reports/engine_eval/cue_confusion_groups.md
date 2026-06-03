# Cue Confusion Groups

These are bootstrap-only synthetic confusion findings. They are not human-reviewed accuracy, model-quality, or production-readiness claims.

- Result rows: `5000`

## ambiguity_vs_unclear_ask

- Cues: `ambiguity, indirect_ask, unclear_ask, vague_timing`
- Suggested precedence rule: Ambiguity should stay observable wording; do not infer avoidance or hidden motive.
- Unexpected within group: `{'ambiguity': 79}`
- Missing within group: `{'ambiguity': 79, 'unclear_ask': 79}`
- Substitutions: `{}`
- Co-fires: `{}`

## conflict_vs_pressure

- Cues: `blame_language, conflict, pressure`
- Suggested precedence rule: Conflict wording should not label a person or become pressure without obligation or constrained-choice wording.
- Unexpected within group: `{}`
- Missing within group: `{'conflict': 100}`
- Substitutions: `{}`
- Co-fires: `{}`

## contradiction_vs_deception

- Cues: `commitment_mismatch, contradiction_against_prior_message, unsupported_claim_shift`
- Suggested precedence rule: Contradiction and commitment mismatch must never imply lying or deception certainty.
- Unexpected within group: `{}`
- Missing within group: `{'contradiction_against_prior_message': 237, 'unsupported_claim_shift': 79}`
- Substitutions: `{}`
- Co-fires: `{}`

## hedging_vs_softening

- Cues: `hedging, reassurance, softening`
- Suggested precedence rule: Softening and reassurance should not imply anxiety, attraction, or attachment style.
- Unexpected within group: `{'hedging': 416}`
- Missing within group: `{'hedging': 67, 'reassurance': 280}`
- Substitutions: `{}`
- Co-fires: `{}`

## reassurance_vs_warmth

- Cues: `alignment, reassurance, repair_opportunity, warmth`
- Suggested precedence rule: Warm or reassuring wording should stay communication-pattern evidence, not emotional truth.
- Unexpected within group: `{}`
- Missing within group: `{'alignment': 79, 'reassurance': 280}`
- Substitutions: `{}`
- Co-fires: `{'alignment+repair_opportunity': 79}`

## specificity_vs_directness

- Cues: `directness, specificity, specificity_drop`
- Suggested precedence rule: Specific detail is not directness unless it includes a clear ask, answer, decision, or commitment.
- Unexpected within group: `{'directness': 911, 'specificity': 936, 'specificity_drop': 146}`
- Missing within group: `{'directness': 67, 'specificity': 280, 'specificity_drop': 158}`
- Substitutions: `{'directness_predicted_when_specificity_expected': 146, 'specificity_drop_predicted_when_specificity_expected': 67}`
- Co-fires: `{'directness+specificity': 1036, 'directness+specificity_drop': 67, 'specificity+specificity_drop': 79}`

## topic_shift_vs_evasion

- Cues: `answer_evasion_pattern, topic_shift`
- Suggested precedence rule: Topic shift should become answer evasion only when it follows an immediately relevant direct question.
- Unexpected within group: `{'answer_evasion_pattern': 258}`
- Missing within group: `{'answer_evasion_pattern': 79}`
- Substitutions: `{}`
- Co-fires: `{'answer_evasion_pattern+topic_shift': 237}`

## urgency_vs_pressure

- Cues: `boundary_pressure, pressure, urgency`
- Suggested precedence rule: Urgency alone should not become pressure unless wording reduces the recipient's response space.
- Unexpected within group: `{'boundary_pressure': 79, 'urgency': 258}`
- Missing within group: `{'urgency': 225}`
- Substitutions: `{}`
- Co-fires: `{'boundary_pressure+pressure+urgency': 337}`
