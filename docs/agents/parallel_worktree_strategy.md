# Parallel Worktree Strategy

Status: branch/worktree guidance for agentic Vibe Signal sprints.

## When To Use Worktrees

Use separate worktrees when engine, UI, deployment, and docs work can progress independently. Keep one agent per worktree when possible.

## Suggested Branch Split

- `codex/engine-<scope>`: cue taxonomy, synthetic regression, reports, engine tests.
- `codex/backend-<scope>`: API contract, CORS, backend tests, smoke scripts.
- `codex/ui-<scope>`: web/mobile UI, accessibility, screenshots, UI tests.
- `codex/recruiter-<scope>`: README, repo tour, project summary.
- `codex/release-gate-<scope>`: closed-beta reports, legal/privacy packet references, QA evidence templates.

## Isolation Rules

- Engine branch does not touch README/UI.
- UI branch does not touch engine.
- Recruiter docs branch merges last.
- Release-gate branch should follow deploy fixes.
- Deployment branch does not run load-heavy production checks.

## Validation Before Merge

Each branch runs its agent-specific commands. The integration branch or final PR runs `bash scripts/dev_check_all.sh`, safety scanners, and any manual smoke scripts required by scope.

## Data Rules

No worktree may introduce raw private chats, tester messages, external dataset rows, secrets, analytics SDKs, or user/tester training data.
