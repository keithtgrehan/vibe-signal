# Vibe Human Review Guidelines

Human reviewers decide labels. Machine cues are suggestions for communication-pattern review only.

## Review Rules

- Accepted labels need evidence spans with `evidence_text`, `evidence_start`, and `evidence_end`.
- Use the narrowest observable label that fits the text.
- Keep `neutral` rows when no communication-pattern label is supported.
- Prefer `unknown` direction or speaker role when the span is ambiguous.
- Do not promote external dataset rows into product gold labels automatically.

## Safety Boundaries

- No emotion, deception, intent, diagnosis, attraction, attachment-style, protected-trait, or neurodivergence claims.
- Do not label someone as manipulative, abusive, autistic, ADHD, dishonest, attracted, attached, or mentally unwell.
- Dataset labels are annotator judgments, not truth.
- Gold labels are reviewed communication-pattern annotations, not hidden-state claims.
