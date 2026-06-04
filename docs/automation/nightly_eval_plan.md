# Nightly Eval Plan

Status: automation design. This does not claim production readiness, human-reviewed accuracy, or legal/privacy approval.

## Run On Each PR

- Python compile and tests.
- Web tests and build.
- Mobile tests and public Expo config where dependencies are available.
- Public-copy safety scanner.
- No-raw-content scanner.
- Restricted-artifact staged check.
- Small synthetic engine smoke only.

## Run Nightly Or Manually

- Full 10k synthetic regression.
- Split-aware hard-negative evaluation.
- Bootstrap metrics by split/cue/scenario.
- Confusion groups.
- False-positive and false-negative analysis.

## Manual Only

- Production smoke against Render.
- Closed-beta gate.
- Deployed-version verification for a release candidate.
- Real-device TestFlight QA.
- Legal/privacy review.
- Human-reviewed label import/adjudication.

## Never Run Automatically

- Production load-heavy 10k evaluation.
- External dataset download or training.
- ML training.
- Raw private chat ingestion.
- User/tester chat training.
- Analytics SDK collection.

## Report Location

Use `reports/engine_eval/` for intentional engine reports and `reports/automation/` for generated gate or local automation output. Avoid committing bulky generated reports unless the PR is explicitly an evaluation/report PR.
