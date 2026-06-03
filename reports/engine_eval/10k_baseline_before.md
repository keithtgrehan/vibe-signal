# 10k Engine Evaluation Baseline Before Changes

Status: baseline captured before split-aware 10k evaluation changes. These are bootstrap-only synthetic regression results, not accuracy, model-quality, production-readiness, cheating-detection, hidden-intent, attraction, deception-certainty, diagnosis, or therapy-support claims.

## Main State

- Branch: `codex/engine-10k-hard-negative-eval`
- Main commit: `715c26e43348518985cf6dfa21d4d79c831355d1`
- Latest observed merge commits:
  - `715c26e` - Add safe status deploy metadata (#26)
  - `7c9410c` - Verify post-merge engine precision baseline (#25)
  - `f7bf447` - Verify post-merge engine precision baseline (#24)
  - `22aa560` - Polish trust-first UI and synthetic demo flow (#23)
  - `8b13108` - Tighten synthetic cue precision regression (#22)

## Artifact Presence Checked

- PR #22 engine precision artifacts: present
  - `reports/engine_eval/synthetic_regression_report.md`
  - `tools/run_synthetic_fixture_regression.py`
  - targeted cue precision tests
- PR #25 verification artifacts: present
  - `reports/engine_eval/postmerge_precision_verification.md`
  - deployed bounded sample reports
- PR #26 deploy metadata artifacts: present
  - `/api/status` fields: `git_commit`, `deploy_version`, `build_timestamp`, `service_revision`
  - `docs/proof/closed_beta/backend_status_metadata.md`

## Commands

- `python -m py_compile $(git ls-files '*.py')`: passed
- `python -m pytest -q`: passed
- `python tools/generate_synthetic_whatsapp_fixtures.py --messages 1000 --no-api`: passed
- `VIBE_SIGNAL_API_URL=http://localhost:5050 python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/conversations.jsonl`: passed
- `python tools/analyze_cue_false_positives.py --results reports/engine_eval/synthetic_regression_results.jsonl`: passed
- `python tools/evaluate_reviewed_cue_labels.py --labels data/review/seed_reviewed_labels.jsonl --results reports/engine_eval/synthetic_regression_results.jsonl --report-out reports/engine_eval/baseline_reviewed_label_evaluation.md --metrics-out reports/engine_eval/baseline_reviewed_label_metrics.json`: passed
- `curl -s http://localhost:5050/api/status`: passed with configured local test metadata

## Baseline Results

- Current fixture count: `1000` synthetic messages / `455` conversations
- Local synthetic API regression: `455/455`
- API transport failures: `0`
- Evidence completeness: `455/455`
- Unsafe-output block rate: `455/455`
- Low-signal fallback correctness: `455/455`
- Missing expected cues: `0`
- Unexpected cues: `0`
- Bootstrap micro precision: `0.6304`
- Bootstrap micro recall: `1.0`
- Human-reviewed status: `not human-reviewed`

## Notes

- This baseline uses synthetic bootstrap labels only.
- Held-out, hard-negative, and red-team split-aware evaluation did not exist before this sprint.
- Future deployed verification can compare `/api/status.git_commit` with the intended deployed commit once Render sets safe commit metadata.
