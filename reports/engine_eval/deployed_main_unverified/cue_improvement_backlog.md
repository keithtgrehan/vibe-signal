# Cue Improvement Backlog

This backlog is generated from synthetic API regression findings. It is not an accuracy claim.

## Candidate False Negatives

- Decide whether `/api/analyze` should expose match-specific cues such as answer evasion, specificity drop, contradiction, and unsupported claim shifts.
- Add API-level evidence spans before treating any missing cue as an engine bug.

## Next Fixture Types

- Direct ask without deadline.
- Deadline without pressure.
- Reassurance without identity or anxiety labels.
- Commitment change with explicit explanation.
- Topic shift that is normal rather than evasive.
