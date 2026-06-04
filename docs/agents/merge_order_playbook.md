# Merge Order Playbook

Status: branch sequencing guide for Vibe Signal. This is not a release approval.

## Recommended Merge Order

1. Engine/core changes.
2. Backend/API contract changes.
3. UI changes.
4. Docs/recruiter updates.
5. Release-gate docs.
6. Deployment verification.

## Why This Order

Engine and backend contracts define result shape and safety behavior. UI should follow stable contracts. Recruiter docs and release gates should describe the final merged state. Deployment verification should happen after the code intended for deploy is merged.

## Branch Rules

- Engine branches do not touch README/UI unless documenting generated reports.
- Backend branches do not change visual presentation unless API copy requires it.
- UI branches do not change engine cue behavior.
- Recruiter docs merge late so they reflect current repo state.
- Release-gate branches follow deploy fixes.
- Deployment verification branches stay bounded to env docs, smoke scripts, and metadata checks.

## Conflict Handling

If two branches need the same file, merge the lower-level branch first and rebase or regenerate the higher-level doc branch. Do not force-push shared work, hard-reset user work, or hide generated report differences.

## Manual Gates

Manual gates can block merge readiness even when automated checks pass. Document them as pending rather than solving them in code.
