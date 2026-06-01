# Vibe Embedding Experiment Plan

This experiment is optional and research-only. It compares pairwise embedding similarity against synthetic communication-fit labels to test whether a future ranking scaffold is worth reviewing.

Rules:

- Use only `data/vibe_matching/synthetic/synthetic_match_pairs.jsonl`.
- Never download models.
- Never download datasets.
- Never call providers.
- If `sentence-transformers` or the requested model is unavailable locally, write a `SKIPPED` report.
- Do not use the output for production routing or launch claims.

Blocked claims:

- deception
- attraction
- diagnosis
- hidden intent
- neurotype
- attachment style
- emotional truth
- response optimization
