# Observable Cue Taxonomy

Vibe Engine labels observable communication-pattern cues only.

| Cue | Observable Evidence | Limit |
| --- | --- | --- |
| `clarity_issue` | Missing concrete next step, vague reference, overloaded wording | Does not infer cognitive state |
| `hedging_shift` | More or fewer hedging markers across spans | Does not infer true emotion |
| `specificity_shift` | More or fewer time, place, action, or detail markers | Does not infer honesty |
| `directness_shift` | More or fewer direct asks or direct answers | Does not infer intent |
| `reassurance_request` | Explicit request for confirmation or reassurance | Does not infer attachment style |
| `pressure_language` | Urgency, ultimatum, or demand wording | Does not score manipulation |
| `boundary_violation` | Text that disregards a stated limit | Does not diagnose either person |
| `repair_attempt` | Apology, reset, clarification, or next-step repair | Does not predict outcome |
| `topic_shift` | Abrupt topic change markers | Does not claim avoidance motive |
| `potential_overload` | Dense, multi-ask, hard-to-scan text | Does not infer neurodivergence |
| `neutral` | No supported cue | Preserves false-positive checks |

## R4 Runtime Fixture Status

The R4 synthetic cue taxonomy fixture pack lives at `tests/fixtures/cue_taxonomy/cue_taxonomy_cases.json`. It covers directness, specificity, hedging, urgency, reassurance, pressure, conflict, alignment, topic shifts, ambiguity, cognitive load, escalation risk, boundary pressure, consent clarity, response timing, and quoted text exclusion.

`src/vibesignal_ai/features/cue_taxonomy.py` implements a minimal deterministic detector for these cue IDs. It uses regex and simple metrics only, excludes quoted lines and code blocks, suppresses response timing when timestamps are missing, and emits evidence objects with interpretation limits.
