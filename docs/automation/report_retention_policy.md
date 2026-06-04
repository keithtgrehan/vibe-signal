# Report Retention Policy

Status: generated-artifact policy for Vibe Signal automation.

## Keep In Git When Intentional

- Small docs that explain current repo state.
- Reviewed synthetic evaluation summaries that are part of an evaluation PR.
- Metadata-only smoke proof needed for a release-gate PR.
- Human-review templates that contain no private chats.

## Do Not Commit By Default

- Large generated JSONL reports from ad hoc local runs.
- Production smoke logs beyond metadata summaries.
- Temporary gate reports from local experiments.
- Screenshots unless they are intentional docs assets.
- Any file containing raw private chats, tester messages, secrets, provider responses, or external dataset rows.

## Suggested Locations

- `reports/engine_eval/`: intentional synthetic regression reports.
- `reports/automation/`: local automation/gate outputs, usually not committed unless scoped.
- `docs/proof/closed_beta/`: curated metadata-only proof for release-gate PRs.
- `docs/assets/screenshots/`: reviewed screenshots only.

## Avoiding Generated Clutter

Before opening a PR:

```bash
git status --short
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --stat
```

If a generated artifact is not needed for review, leave it unstaged or regenerate it in a separate report PR.

## Avoiding False Claims

Generated reports may describe synthetic regression or bootstrap metrics. They must not claim production readiness, legal/privacy compliance, App Store readiness, real-world NLP accuracy, or human-reviewed quality unless the matching human gate has passed.
