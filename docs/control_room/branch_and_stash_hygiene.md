# Branch And Stash Hygiene

Status date: 2026-06-08.

Purpose: give Keith a safe cleanup plan without deleting branches, applying stashes, or mixing research work into production/demo branches.

This document is instructions only. No destructive branch or stash command was run for this control-room pass.

## List Branches

```bash
git branch --list
git branch --remote
git branch --all
```

To see local branches with last commit and upstream:

```bash
git branch -vv
```

## Identify Merged Branches

After updating `main`:

```bash
git checkout main
git pull origin main
git branch --merged main
```

Review the output manually. Do not delete branches just because they appear in this list if they are being preserved for audit or have an open PR.

## Delete Local Merged Branches Safely

Use only after manual review:

```bash
git branch -d <branch-name>
```

Use `-d`, not `-D`, for normal cleanup. If Git refuses deletion, treat that as a signal to inspect why the branch is not fully merged.

Do not delete remote branches until their PRs are merged, closed, or intentionally preserved.

## Preserve Research Branches Before Deletion

If a branch contains research direction worth preserving, create a docs-only recovery note first:

```bash
git checkout main
git pull origin main
git checkout -b codex/<topic>-research-audit
```

Then recover only high-level direction, filenames, validation notes, and safe next actions. Do not copy raw private data, raw-message fixtures, generated artifacts, model files, embeddings, or training outputs.

## List Stashes Without Applying Them

Safe first command:

```bash
git stash list --date=local
```

This shows stash names and timestamps only. For this control-room pass, stash contents were not inspected, applied, popped, merged, or copied.

If Keith later wants metadata-only inspection before creating a branch, use filename/stat commands and treat filenames as potentially sensitive:

```bash
git stash show --stat stash@{0}
git stash show --name-only stash@{0}
```

Do not use patch inspection in public PR notes if the stash may contain private or raw content. Prefer creating a dedicated audit branch rather than applying it to an active branch.

## Create A Branch From A Stash Safely

Use a dedicated branch name and the exact stash reference Keith wants to audit:

```bash
git stash branch codex/research-stash-audit-synthetic-engine stash@{0}
```

This is safer than `git stash pop` because it isolates the stash on its own branch. Run safety checks before committing anything from that branch.

## Do Not Pop Into These Branches

Do not run `git stash pop` or `git stash apply` on:

- `main`
- CEO-demo or recruiter-demo branches
- production/deployment branches
- release branches
- any branch with unrelated dirty work

## Recommended Cleanup Order

1. Merge or close the current documentation/control-room PR.
2. Confirm PR #46 and PR #66 are closed as superseded.
3. Re-check open PRs with `gh pr list --state open`.
4. Decide whether PR #45 is still needed after custom-domain CORS is fixed.
5. Decide whether PR #42, #41, and #40 still have value after the control-room docs land.
6. Audit private WhatsApp and synthetic research branches only through fresh docs-only branches.
7. Audit stashes one at a time through `git stash branch`, never by popping into `main`.
8. Delete only local merged branches that have no open PR and no preserved research value.
9. Defer remote branch deletion until the matching PR is merged, closed, or intentionally preserved.

## Validation Before Any Cleanup PR

For docs-only cleanup:

```bash
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
python -m pytest tests/test_public_copy_safety.py tests/test_private_data_hygiene.py -q
git diff --check
```
