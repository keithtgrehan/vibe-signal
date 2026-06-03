# Blocked Inferences And False-Positive Risks

## Blocked Inferences

Vibe Signal must not infer:

- private feelings
- hidden motives
- attraction
- deception certainty
- cheating or betrayal verdicts
- diagnosis
- neurotype
- personality labels
- relationship-style labels
- emotional truth
- whether someone will reply
- whether the user should pressure or influence someone

## Product Redirect

When a user requests a blocked inference, redirect to observable wording:

```text
I cannot determine private feelings, motives, diagnosis, or outcomes from this text. I can review observable wording patterns, evidence phrases, uncertainty, and safer clarification options.
```

## False-Positive Risk Register

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| short text overread | little evidence creates false certainty | low-signal fallback |
| urgency vs pressure | real deadlines can be urgent without coercion | separate cue IDs |
| reassurance vs pathology | care checks are not diagnosis | cannot-infer block |
| contradiction vs deception | changed wording does not prove lying | commitment mismatch wording |
| boundary pressure vs direct ask | a direct request can be respectful | require boundary/pressure evidence |
| ambiguity vs avoidance | missing context may be shared context | ask for clarification |
| conflict vs diagnosis | escalation is wording, not identity | block person labels |
| softener vs weakness | politeness varies by culture | label wording only |
| topic shift vs evasion | ordinary conversation can drift | mixed/low signal |
| synthetic regression vs accuracy | fixtures are not population validation | no model-quality claims |
