# Production Smoke Deploy-Status Automation Handoff

Status: master control-room handoff for the deploy-status automation patch merged in PR #34.

Last updated: 2026-06-06 01:12:08 CEST.

## Repository And PR Facts

- Repository: `keithtgrehan/vibe-signal`
- Original patch branch: `codex/fix-prod-smoke-wrapper-deploy-status`
- Original patch commit: `6cff7fcd9a63e331127ab70a83594b874636cfed`
- Original PR: https://github.com/keithtgrehan/vibe-signal/pull/34
- PR #34 title: `Fix production smoke deploy-status automation`
- PR #34 state observed on 2026-06-06: `MERGED`
- Current documentation branch for this file: `codex/add-prod-smoke-control-room-handoff`
- Current `origin/main` observed while writing this file: `c408e08994f2489a2e24cb366442650e9f9b65bb`

## What Was Fixed

PR #33 added production and closed-beta automation wrappers, but two wrapper behaviors were incomplete:

1. `scripts/prod_smoke_all.sh` only passed `--expected-git-commit` to `scripts/verify_deployed_version.py` when `EXPECTED_GIT_COMMIT` was manually supplied.
2. `scripts/closed_beta_gate_all.sh` defaulted deploy status to `unverified` instead of deriving `current`, `stale`, or `unverified` from deployed metadata.
3. Routine closed-beta wrapper runs wrote generated reports in a way that could leave tracked report files dirty when operators only wanted to run the gate.

The patch makes wrapper behavior match the release gate:

- Production smoke auto-uses the local git SHA by default.
- Closed-beta gate derives deploy status from the verifier.
- Routine generated reports stay in ignored automation output by default.
- Tracked gate reports are refreshed only when intentionally requested.
- Safety scanners, deploy verification, and tester-invite blocking semantics remain intact.

## Files Changed By PR #34

- `scripts/prod_smoke_all.sh`
- `scripts/closed_beta_gate_all.sh`
- `tests/test_automation_wrappers.py`
- `docs/automation/manual_workflow_plan.md`
- `docs/deployment/render_deploy_metadata.md`

This handoff file was added after PR #34 so the master control room has the operational and implementation detail in one place.

## Hard Boundaries Preserved

The patch does not:

- weaken safety scanners
- bypass deployed-version verification
- force deploy status to `current`
- hide stale deployments
- claim tester invites are allowed
- add ML, datasets, analytics, paywalls, providers, engine logic, or UI changes
- make claims about cheating detection, hidden intent, attraction prediction, lie detection, diagnosis, therapy, manipulation, model quality, production readiness, legal compliance, or App Store release

The deployed-version verifier prints only allowlisted metadata fields:

- `git_commit`
- `deploy_version`
- `build_timestamp`
- `service_revision`

It does not expose secrets, raw environment dumps, request bodies, private chats, local paths, usernames, tokens, or user content.

## Production Smoke Wrapper Behavior

File: `scripts/prod_smoke_all.sh`

### Inputs

- Positional arg 1: production base URL.
- Default base URL: `https://vibe-signal.onrender.com`, via `DEFAULT_PROD_BASE_URL` from `scripts/_automation_common.sh`.
- Environment override: `VIBE_SIGNAL_PROD_BASE_URL`.
- Expected commit override: `EXPECTED_GIT_COMMIT`.
- Python executable override: `PYTHON`.

### Expected Commit Resolution

The wrapper computes:

```bash
EXPECTED_GIT_COMMIT="${EXPECTED_GIT_COMMIT:-$(git rev-parse HEAD 2>/dev/null || true)}"
```

Meaning:

- If `EXPECTED_GIT_COMMIT` is set, that value wins.
- Otherwise, the wrapper uses the current repo `HEAD`.
- If the script is run outside a git checkout, the command resolves to an empty string without failing the wrapper only for that reason.

### Verifier Command When Expected Commit Exists

When `EXPECTED_GIT_COMMIT` is non-empty, production smoke runs deployed-version verification with retry:

```bash
python scripts/verify_deployed_version.py \
  --base-url "$BASE_URL" \
  --timeout-seconds 30 \
  --expected-git-commit "$EXPECTED_GIT_COMMIT"
```

Actual wrapper uses:

```bash
run_required_with_retry "Deployed version verification" 2 2 "$PYTHON_BIN" scripts/verify_deployed_version.py --base-url "$BASE_URL" --timeout-seconds 30 --expected-git-commit "$EXPECTED_GIT_COMMIT"
```

Retry behavior is preserved:

- 2 attempts
- 2 seconds between attempts
- no retry semantics were weakened

### Verifier Command When Expected Commit Is Missing

If no expected SHA is available, the wrapper prints:

```text
Expected git commit unavailable; deployed version proof may be unverified.
```

Then it runs:

```bash
python scripts/verify_deployed_version.py \
  --base-url "$BASE_URL" \
  --timeout-seconds 30
```

This can produce deploy status `unverified`. It does not pretend the deploy is current.

### Production Analyze Smoke

After deployed-version verification passes, the wrapper runs:

```bash
python scripts/smoke_test_production_analyze.py --base-url "$BASE_URL"
```

Important: if deploy verification is `stale` or the endpoints fail, `prod_smoke_all.sh` stops before production analyze smoke because `run_required_with_retry` returns non-zero.

### Exit Semantics

- `current`: verifier exits 0, wrapper continues to production analyze smoke.
- `unverified`: verifier generally exits 0 if endpoints are healthy but expected commit is missing; wrapper can continue, but deploy proof is explicitly unverified.
- `stale`: verifier exits 1; wrapper fails and does not continue.
- health/status endpoint failure: verifier exits 1; wrapper fails.

Production smoke success is not equivalent to deployed commit proof. Deploy proof is only `current` when `/api/status.git_commit` matches the expected SHA.

## Closed-Beta Gate Wrapper Behavior

File: `scripts/closed_beta_gate_all.sh`

### Inputs

- Positional arg 1: production base URL.
- Default base URL: `https://vibe-signal.onrender.com`.
- Environment override: `VIBE_SIGNAL_PROD_BASE_URL`.
- Expected commit override: `EXPECTED_GIT_COMMIT`.
- Report output override: `CLOSED_BETA_GATE_REPORT_OUT`.
- Tracked report mode: `WRITE_REPORT=1`.
- Python executable override: `PYTHON`.

### Expected Commit Resolution

Closed-beta gate computes:

```bash
EXPECTED_GIT_COMMIT="${EXPECTED_GIT_COMMIT:-$(git rev-parse HEAD 2>/dev/null || true)}"
```

This matches production smoke behavior.

### Default Report Path

Routine wrapper output goes to:

```text
reports/automation/latest/closed_beta_gate_report.md
```

The repository ignores `reports/automation/`, so routine wrapper runs do not dirty tracked report files.

### Tracked Report Path

Tracked report output is:

```text
docs/proof/closed_beta/closed_beta_gate_report.md
```

To intentionally update the tracked report, run:

```bash
WRITE_REPORT=1 bash scripts/closed_beta_gate_all.sh
```

If `CLOSED_BETA_GATE_REPORT_OUT` is set, that explicit path wins over both defaults.

### Deploy Status Derivation

The wrapper runs the verifier in JSON mode:

```bash
python scripts/verify_deployed_version.py \
  --base-url "$BASE_URL" \
  --timeout-seconds 30 \
  --format json \
  --expected-git-commit "$EXPECTED_GIT_COMMIT"
```

If `EXPECTED_GIT_COMMIT` is missing, it omits `--expected-git-commit` and prints the same warning used by production smoke.

The verifier output is captured to a temporary file from `mktemp`, printed to stdout, parsed, and then removed.

The parser extracts:

```json
"version_status": "current"
```

Allowed parsed values:

- `current`
- `stale`
- `unverified`

Any missing, malformed, or unexpected value falls back to `unverified` and prints:

```text
Deployed version status could not be parsed; using unverified.
```

### Non-Zero Verifier Handling

The closed-beta wrapper does not treat a `stale` verifier exit as a shell failure, because `stale` is real evidence that must be passed into the gate checker.

This is deliberate:

- `prod_smoke_all.sh` fails on `stale`.
- `closed_beta_gate_all.sh` records `stale` as gate evidence and lets the gate report show `MANUAL_REQUIRED`.

### Gate Checker Invocation

After deriving deploy status, the wrapper runs:

```bash
python scripts/closed_beta_gate_check.py \
  --deploy-status "$DEPLOY_STATUS" \
  --report-out "$REPORT_OUT"
```

The deploy status passed to the checker is never hardcoded to `current`.

### Tester Invite Decision

The wrapper checks the generated report for blocking/manual-required language:

```bash
rg -q "Tester invites remain .*BLOCKED|BLOCKED|MANUAL_REQUIRED" "$REPORT_OUT"
```

If found, it prints:

```text
Tester invite decision: BLOCKED_OR_MANUAL_REQUIRED. Human/legal/device gates still control release.
```

Otherwise, it prints:

```text
Tester invite decision: REVIEW_REQUIRED. A human owner must approve any tester invite.
```

This script never claims tester invites are allowed.

## Deploy Status Definitions

From `scripts/verify_deployed_version.py`:

- `current`: `/healthz` and `/api/status` are healthy, `/api/status.git_commit` exists, and it matches the expected SHA.
- `stale`: `/healthz` and `/api/status` are healthy, `/api/status.git_commit` exists, and it does not match the expected SHA.
- `unverified`: metadata is missing, endpoints fail, or no expected SHA was supplied.

## Operator Runbook

### Check Current Local SHA

```bash
git rev-parse HEAD
```

Use this SHA as the expected deployment commit unless you deliberately override `EXPECTED_GIT_COMMIT`.

### Run Direct Deploy Verification

```bash
python scripts/verify_deployed_version.py \
  --base-url https://vibe-signal.onrender.com \
  --expected-git-commit "$(git rev-parse HEAD)"
```

Use this when you only need deploy metadata proof.

### Run Production Smoke

```bash
bash scripts/prod_smoke_all.sh https://vibe-signal.onrender.com
```

Expected successful flow:

1. Deployed-version verification reports `current`.
2. Production analyze smoke runs with synthetic payloads.
3. Wrapper prints `Production smoke complete`.

If deployed-version verification reports `stale`, stop and redeploy/configure Render before treating the production smoke as complete.

### Run Closed-Beta Gate

```bash
bash scripts/closed_beta_gate_all.sh https://vibe-signal.onrender.com
```

Expected behavior:

- The wrapper derives deploy status from deployed metadata.
- It writes a routine report to `reports/automation/latest/closed_beta_gate_report.md`.
- It does not dirty tracked gate reports.
- Tester invites remain blocked unless manual gates are truly complete.

### Intentionally Refresh Tracked Gate Report

Only do this when a tracked proof report update is wanted:

```bash
WRITE_REPORT=1 bash scripts/closed_beta_gate_all.sh https://vibe-signal.onrender.com
```

Then inspect:

```bash
git diff -- docs/proof/closed_beta/closed_beta_gate_report.md
```

Do not commit timestamp-only tracked report churn.

### Override Expected Commit Manually

Use only when verifying a specific SHA:

```bash
EXPECTED_GIT_COMMIT=<expected-main-sha> bash scripts/prod_smoke_all.sh https://vibe-signal.onrender.com
```

or:

```bash
EXPECTED_GIT_COMMIT=<expected-main-sha> bash scripts/closed_beta_gate_all.sh https://vibe-signal.onrender.com
```

### Override Report Path

```bash
CLOSED_BETA_GATE_REPORT_OUT=/tmp/closed_beta_gate_report.md bash scripts/closed_beta_gate_all.sh
```

This explicit path wins over both default latest output and `WRITE_REPORT=1`.

### Run Outside A Git Checkout

The wrappers can run outside a git repo, but deploy proof may be `unverified` because no expected SHA can be derived.

Expected warning:

```text
Expected git commit unavailable; deployed version proof may be unverified.
```

Do not treat that as deployed commit proof.

## Render Configuration Runbook

Render must expose safe metadata through `GET /api/status`.

Set non-secret backend environment variables:

```text
GIT_COMMIT=<expected-main-sha>
DEPLOY_VERSION=<human-readable-version>
BUILD_TIMESTAMP=<utc-build-timestamp>
SERVICE_REVISION=<render-or-release-label>
```

Example shape:

```text
GIT_COMMIT=c408e08994f2489a2e24cb366442650e9f9b65bb
DEPLOY_VERSION=main-2026-06-06
BUILD_TIMESTAMP=2026-06-06T00:00:00Z
SERVICE_REVISION=render-main
```

If Render supplies `RENDER_GIT_COMMIT`, the backend can accept that as fallback for `git_commit`.

Do not expose:

- secrets
- API keys
- tokens
- full environment dumps
- internal URLs
- local paths
- usernames
- request bodies
- private chats
- raw user content

After changing Render env vars, redeploy the backend, then run:

```bash
python scripts/verify_deployed_version.py \
  --base-url https://vibe-signal.onrender.com \
  --expected-git-commit "$(git rev-parse HEAD)"
```

The release gate should only consider deploy proof complete when this reports:

```text
Version status: `current`
```

## Latest Live Deploy Observation

Observed from this control-room branch on 2026-06-06:

```text
Expected git commit: c408e08994f2489a2e24cb366442650e9f9b65bb
Render git_commit: 30a3b97d2454c14c7d2c4f690fe0df9657e31d66
Render deploy_version: main-2026-06-04
Render build_timestamp: 2026-06-04T21:05:00Z
Render service_revision: render-main
Version status: stale
Reason: git_commit_does_not_match_expected
Health endpoint: PASS
Status endpoint: PASS
```

This status is time-sensitive. Re-run the verifier before making any deployment decision.

## Test Coverage Added

File: `tests/test_automation_wrappers.py`

The tests use a temporary fake Python executable so wrapper behavior can be tested without network calls or real scanner execution.

### Test: Production Smoke Passes Current Git Commit Inside Repo

Test name:

```text
test_prod_smoke_passes_current_git_commit_inside_repo
```

Checks:

- runs `bash scripts/prod_smoke_all.sh https://example.invalid`
- stubs Python script calls
- reads local `git rev-parse HEAD`
- asserts verifier call includes `--expected-git-commit`
- asserts value equals repo `HEAD`

### Test: Production Smoke Warns And Falls Back Outside Git Repo

Test name:

```text
test_prod_smoke_warns_and_falls_back_outside_git_repo
```

Checks:

- copies wrapper scripts into a temporary non-git directory
- stubs required Python files
- runs production smoke there
- asserts warning is printed:

```text
Expected git commit unavailable; deployed version proof may be unverified.
```

- asserts verifier call does not include `--expected-git-commit`

### Test: Closed-Beta Gate Passes Stale Deploy Status

Test name:

```text
test_closed_beta_gate_passes_stale_deploy_status_to_checker
```

Checks:

- fake verifier prints JSON with `version_status: stale`
- fake verifier exits non-zero
- wrapper still calls `closed_beta_gate_check.py`
- checker receives `--deploy-status stale`

This proves the wrapper does not hide stale deploys and does not force `current`.

### Test: Closed-Beta Gate Passes Unverified Deploy Status

Test name:

```text
test_closed_beta_gate_passes_unverified_deploy_status_to_checker
```

Checks:

- fake verifier prints JSON with `version_status: unverified`
- checker receives `--deploy-status unverified`

This proves production smoke success alone is not being used as deploy proof.

### Test: Default Report Does Not Touch Tracked Report

Test name:

```text
test_closed_beta_gate_default_report_does_not_touch_tracked_report
```

Checks:

- records contents of `docs/proof/closed_beta/closed_beta_gate_report.md`
- runs closed-beta wrapper with fake verifier status `current`
- asserts tracked report contents are unchanged
- asserts checker receives `--deploy-status current`
- asserts default report path is `reports/automation/latest/closed_beta_gate_report.md`

## Validation From PR #34

Validation run during the patch:

```bash
python -m py_compile $(git ls-files '*.py')
python -m pytest -q
bash scripts/prod_smoke_all.sh
bash scripts/closed_beta_gate_all.sh
bash scripts/dev_check_all.sh
python scripts/verify_deployed_version.py --base-url https://vibe-signal.onrender.com --expected-git-commit "$(git rev-parse HEAD)"
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
git diff --check
git status --short
```

Results observed during PR #34:

- Python compile passed.
- Full pytest passed.
- Focused wrapper tests passed.
- `dev_check_all.sh` passed after installing ignored `web/node_modules` and `mobile/node_modules` with `npm ci`.
- Public-copy safety scanner passed.
- No-raw-content leak scanner passed.
- Git whitespace check passed.
- Production smoke failed on live deploy status `stale`, which was correct because Render was not on the expected SHA.
- Closed-beta gate passed and recorded deploy status `stale`, with tester invite decision still blocked.
- `git status --short` after wrapper runs showed no tracked generated report diffs.

## Validation To Run After Any Future Edit

Minimum focused validation:

```bash
python -m pytest -q tests/test_automation_wrappers.py tests/test_verify_deployed_version.py tests/test_closed_beta_gate_check.py
bash -n scripts/prod_smoke_all.sh scripts/closed_beta_gate_all.sh
git diff --check
```

Full validation:

```bash
python -m py_compile $(git ls-files '*.py')
python -m pytest -q
bash scripts/dev_check_all.sh
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
git diff --check
```

Live deployment validation:

```bash
python scripts/verify_deployed_version.py \
  --base-url https://vibe-signal.onrender.com \
  --expected-git-commit "$(git rev-parse HEAD)"

bash scripts/prod_smoke_all.sh https://vibe-signal.onrender.com
bash scripts/closed_beta_gate_all.sh https://vibe-signal.onrender.com
git status --short
```

Expected `git status --short` after routine wrappers:

- no tracked generated report changes
- ignored `reports/automation/` output may exist

Check ignored generated output explicitly:

```bash
git status --short --ignored reports/automation docs/proof/closed_beta/closed_beta_gate_report.md
```

## Troubleshooting

### Production Smoke Reports `stale`

Meaning:

- deployed `/api/status.git_commit` exists
- it does not match the expected SHA

Actions:

1. Run `git rev-parse HEAD`.
2. Compare with `/api/status.git_commit` from verifier output.
3. Confirm Render service is deployed from the intended commit.
4. Confirm Render `GIT_COMMIT` or `RENDER_GIT_COMMIT` is correct.
5. Redeploy Render.
6. Re-run direct verifier.

Do not override this by setting deploy status to `current`.

### Production Smoke Reports `unverified`

Possible causes:

- no expected SHA supplied and not inside a git repo
- `/api/status.git_commit` missing
- `/healthz` unavailable
- `/api/status` unavailable
- verifier output cannot prove deployed version

Actions:

1. Run inside a git checkout or set `EXPECTED_GIT_COMMIT`.
2. Check Render metadata env vars.
3. Check `/healthz`.
4. Check `/api/status`.
5. Re-run direct verifier.

Do not treat `unverified` as a release pass.

### Closed-Beta Gate Exits 0 While Deploy Is Stale

This can be expected.

Closed-beta gate records stale deploy proof as `MANUAL_REQUIRED` instead of failing the whole wrapper when safety scanners pass. The report remains blocking for tester invites.

Use the gate matrix, not only the shell exit code, to decide release readiness.

### Tracked Report Is Dirty After Wrapper Run

Check whether the operator used one of these:

```bash
WRITE_REPORT=1
CLOSED_BETA_GATE_REPORT_OUT=docs/proof/closed_beta/closed_beta_gate_report.md
```

If not intentional, do not commit timestamp-only report churn.

Routine path should be:

```text
reports/automation/latest/closed_beta_gate_report.md
```

### `dev_check_all.sh` Fails Because `vite` Is Missing

Install web dependencies:

```bash
cd web
npm ci
cd ..
```

Then rerun:

```bash
bash scripts/dev_check_all.sh
```

### `dev_check_all.sh` Fails Because Expo Plugins Are Missing

Install mobile dependencies:

```bash
cd mobile
npm ci
cd ..
```

Then rerun:

```bash
bash scripts/dev_check_all.sh
```

## Release Gate Interpretation

Deploy status affects the `deployed_backend_version` gate:

- `current`: `PASS`
- `stale`: `MANUAL_REQUIRED`
- `unverified`: `MANUAL_REQUIRED`

Tester invites remain blocked unless all required human and technical gates pass, including:

- real-device iPhone/TestFlight QA evidence
- legal/privacy human review
- human-reviewed labels where required
- deployed backend metadata proving the intended commit
- metadata-only monitoring gate
- public-copy and no-raw-content safety scanners

Automation output does not approve:

- tester invites
- production launch
- App Store release
- legal/GDPR/CCPA compliance
- model quality
- real-world accuracy
- human-reviewed validation

## Maintenance Notes

Keep these invariants if future maintainers edit the wrappers:

1. Do not make production smoke pass when deploy status is `stale`.
2. Do not hardcode closed-beta deploy status to `current`.
3. Do not infer deploy proof from production analyze smoke success.
4. Do not update tracked gate reports by default.
5. Keep generated routine reports under ignored paths.
6. Keep safe metadata allowlisted.
7. Preserve retry behavior in production smoke deployed-version verification.
8. Preserve tester-invite blocking language.
9. Keep wrapper tests isolated from network calls.
10. Re-run focused wrapper tests before merging any wrapper edit.

## Quick Commands

Routine production smoke:

```bash
bash scripts/prod_smoke_all.sh
```

Routine closed-beta gate:

```bash
bash scripts/closed_beta_gate_all.sh
```

Direct deploy proof:

```bash
python scripts/verify_deployed_version.py --base-url https://vibe-signal.onrender.com --expected-git-commit "$(git rev-parse HEAD)"
```

Intentional tracked report refresh:

```bash
WRITE_REPORT=1 bash scripts/closed_beta_gate_all.sh
```

Focused tests:

```bash
python -m pytest -q tests/test_automation_wrappers.py tests/test_verify_deployed_version.py tests/test_closed_beta_gate_check.py
```

Full local gate:

```bash
bash scripts/dev_check_all.sh
```

Post-wrapper cleanliness check:

```bash
git status --short
```

