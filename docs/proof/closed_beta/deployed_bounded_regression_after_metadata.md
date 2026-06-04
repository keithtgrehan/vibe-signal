# Deployed Bounded Regression After Metadata

Status: `RUN`.

This check should run only after `/api/status.git_commit` proves the deployed backend is on the intended main commit.

## Required Commands

```bash
python scripts/verify_deployed_version.py --base-url https://vibe-signal.onrender.com --expected-git-commit <expected-main-sha>
VIBE_SIGNAL_API_URL=https://vibe-signal.onrender.com python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/heldout/conversations.jsonl --limit 100
```

## Current Result

Deployment proof returned `current` for expected commit `b5b4606c9d4842121046c1c3644941fa6ae115fa`.

Bounded deployed held-out sample:

- API URL: `https://vibe-signal.onrender.com`
- Input: `data/synthetic/whatsapp/heldout/conversations.jsonl`
- Limit: `100`
- Evaluated conversations: `100`
- Passed synthetic contract evaluations: `40/100`
- Evidence completeness: `100/100`
- Unsafe-output block: `100/100`
- API transport failures: `0`

Interpretation: deployed transport and safety/evidence gates were healthy for the bounded sample, but the deployed `/api/analyze` contract did not match all held-out synthetic expected cues. This is a synthetic contract regression finding, not a real-world accuracy claim. Tester invites remain blocked.
