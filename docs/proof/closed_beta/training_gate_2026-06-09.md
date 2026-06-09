# Training Gate - 2026-06-09

Status: Passed for closed-beta no-training gate.

Closed-beta decision:

- No model training.
- No new datasets.
- No raw private chats.
- No tester messages.
- No private screenshots.
- Deterministic cue extraction only.
- Synthetic fixtures only.

Commands run:

```bash
python scripts/validate_vibe_training_sources.py --config configs/vibe_training_sources.example.yml --mode research
python scripts/evaluate_closed_beta_fixtures.py --input data/synthetic/closed_beta_qa/closed_beta_qa_fixtures.json --output-md reports/closed_beta_eval/latest.md --output-json reports/closed_beta_eval/latest.json
python -m pytest tests/test_validate_vibe_training_sources.py tests/test_evaluate_closed_beta_fixtures.py tests/test_closed_beta_qa_fixtures.py
```

Results:

- Training-source validation: passed, `16` row(s), `1` research training-ready source, `project_mode=research_only`.
- Closed-beta fixture evaluator: passed, `11` fixture(s), `0` forbidden-output violation(s), `training=false`, `private_data_read=false`.
- Evaluator report summary: `8` cue hits, `7` expected-span hits, `7` required-safe-phrase hits, `1` low-evidence fallback, `3` unclear outputs.
- Targeted pytest command: `27 passed`.

Required evidence covered:

- Dataset registry fails closed outside approved synthetic/research paths.
- Evaluator report states `trained=false`.
- Evaluator report states `private_data_read=false`.
- Forbidden-output violations are zero.

Notes:

- This is not a model-quality, accuracy, or validation claim.
- The `3` unclear outputs are diagnostics for future deterministic engine work, not a closed-beta training signal.
