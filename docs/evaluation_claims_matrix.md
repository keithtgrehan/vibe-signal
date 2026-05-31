# Evaluation Claims Matrix

The claims matrix config controls what Vibe Engine may say before launch. Supported claims must stay evidence-backed and communication-pattern-only. Gated claims require future reviewed labels and evaluation gates. Blocked claims are red-line examples and cannot become product copy.

Allowed claim families:

- directness, specificity, hedging, overload, pressure wording, boundary wording, consent wording, repair opportunity, and topic-shift comparisons;
- local evidence-object navigation for reviewer workflow;
- deletion/export and local-first privacy controls.

Blocked claim families:

- deception, hidden intent, true emotion, attraction, diagnosis, protected-trait inference, workplace or education decisions, biometric analysis, manipulation scoring, production model quality, and statistical-significance claims without a future explicit gate.

Validation:

```bash
python scripts/validate_claims_matrix.py --path configs/claims_matrix.example.yml
```
