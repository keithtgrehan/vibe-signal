# Research Recovery Log

Status date: 2026-06-08.

Purpose: record what was recovered from superseded PRs and what was intentionally not merged. This is a high-level recovery log only. It does not copy implementation diffs, private data, generated artifacts, model outputs, or raw fixtures.

## PR #46 - Safe WhatsApp Dynamics Research Prototype

PR: `https://github.com/keithtgrehan/vibe-signal/pull/46`

Observed status:

- Draft.
- Conflicted.
- 30 changed files.
- Research-heavy local-only/private WhatsApp direction.
- Not merged.

Useful ideas recovered:

- Local-only research prototype direction.
- Aggregate-only reporting.
- Synthetic fixture export concept.
- Weak-label baseline scaffolding concept.
- Optional audio-feature schema must remain bounded feature divergence, not emotion truth.

Rejected or blocked for now:

- Conflicted branch.
- 30 files / large diff.
- Research-heavy scope.
- No direct merge.
- No production runtime change.
- No raw/private data path.
- No model training.
- No generated artifacts copied into `main`.

Recovery action:

- Useful direction is captured in `docs/control_room/research_index.md`.
- Future sequence is captured in `docs/control_room/research_to_execution_roadmap.md`.
- PR #46 was closed as superseded rather than resolved directly.
- Any implementation should be recovered later through a separate research-audit branch from current `main`.

## PR #66 - UI/UX Product Design Research Upgrade

PR: `https://github.com/keithtgrehan/vibe-signal/pull/66`

Observed status:

- Open at inspection time.
- Conflicted.
- 17 changed files.
- Incomplete/vague template body.
- Not merged.

Useful ideas recovered:

- Trust-first UI polish.
- Accessibility/reviewer flow ideas.
- Synthetic demo expansion ideas.

Rejected or blocked for now:

- Conflicted/incomplete PR body.
- Broad diff across web, mobile, docs, and tests.
- PR #67 already shipped the CEO-demo/reviewer-facing subset.
- No direct merge over current `main`.

Recovery action:

- Useful direction is captured as future extraction only.
- Implementation is deferred to smaller clean PRs with complete PR bodies and current `main` baseline.
- PR #66 was closed as superseded by PR #67 plus this control-room consolidation.

## PR #56 And PR #67 Baseline Notes

- PR #56 is already merged and requires no action.
- PR #67 is already merged and is the current recruiter/CEO-demo baseline.
- This recovery pass does not undo either PR.

## Final Recruiter-Readiness Polish Closures

PR #45 was closed as superseded because it only handled the old Replit A/B origin. The current priority is custom-domain CORS for the main Vercel/Render setup, handled separately from docs cleanup.

PR #44 was closed as superseded by the control-room research/audit process. It may contain useful local-only research direction, but future recovery must happen through a dedicated audit branch with no raw private data, no production model training, no runtime behavior changes, and aggregate-only reporting.

PR #42 was closed as a superseded draft experiment. Any future A/B work should start from current `main` in a small clean branch.

PR #41 and PR #40 were closed as superseded docs PRs. Their A/B governance, variant history, and Replit/minimal-UI context are now represented at a higher level through the control-room docs.

## Explicit Non-Recovery

The following were intentionally not recovered or copied:

- raw private chats
- tester messages
- raw-message fixtures
- raw-content screenshots
- external datasets
- embeddings, vectors, checkpoints, or model artifacts
- generated private reports
- production runtime behavior changes
- model training scripts as product behavior
- CORS fixes or deployment changes

## Next Safe Recovery Pattern

For any stale research branch:

1. Start from latest `main`.
2. Create a fresh audit branch.
3. Recover high-level direction, filenames, and safe next actions only.
4. Do not copy raw/private data or generated artifacts.
5. Run safety scanners.
6. Open a small PR with a complete body.
