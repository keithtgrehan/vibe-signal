# Private Data Exposure Audit

Audit date: 2026-06-05.

Status: hygiene audit note for private WhatsApp / gold human-review data handling. This note is not a legal approval, compliance claim, or guarantee. The audit found no exposure in checked surfaces.

## Scope Checked

- Current tracked files in the repository.
- Ignored restricted local paths, including `data/restricted/private_whatsapp/**`.
- Git object/path history scan for raw/export/workbook/model-style private data paths.
- Remote branch path scan for risky private data paths.
- GitHub Actions artifact name scan.
- Web dist grep.
- Backend/API route review for raw private content persistence or response exposure risks.
- Workflow `upload-artifact` review for risky artifact names and paths.

## Findings

- Current tracked files did not contain raw private WhatsApp exports, private workbooks, private models, or private processed JSONL files in the checked surfaces.
- `data/restricted/private_whatsapp/**` is ignored and remains the expected local-only location for restricted private review data.
- Local private files remain under ignored restricted paths and were not added to the tracked repo by this audit note.
- Web dist grep was clean in the checked build output.
- GitHub Actions artifact name scan found no risky artifacts.
- Git history path scan did not show real private raw/export/workbook/model files in the checked path/object surfaces.
- Backend and API route review did not identify intentional raw private chat persistence in tracked code.
- Workflow artifact review did not identify upload-artifact paths intended to publish private WhatsApp raw exports, private workbooks, private models, or private processed JSONL files.

## Remaining Uncertainty

- PR comments and PR body text were not exhaustively reviewed.
- External provider logs are not fully inspectable from the repository.
- Local terminal history, shell history, editor state, chat transcripts, screenshots, and other machine-local history outside the repo are not controlled by git.
- Future manual `git add -f` or equivalent force-adds remain possible.
- Future workflow changes could introduce new artifact paths if they are not reviewed.

## Recommendations

- Private data must remain local-only unless a future rights-reviewed process explicitly approves a narrower path.
- Never force-add `data/restricted/private_whatsapp/**`.
- Keep private WhatsApp exports, workbooks, processed JSONL, and private review outputs out of git, PRs, CI artifacts, screenshots, and demo materials.
- Rename ignored local raw filenames that contain real names to neutral filenames before demos or interviews.
- Optional local-only example: use a neutral ignored filename such as `data/restricted/private_whatsapp/raw/private_whatsapp_export.zip`.
- Do not execute local private-file renames in repo automation without Keith's explicit instruction.
- Avoid real names in tests and fixtures; use neutral synthetic labels such as `Person A` and `Person B`.
- Run an exposure audit before demos, interviews, public screenshots, or reviewer handoff.
- Keep n8n workflows no-raw-content unless explicitly rights-reviewed.
- n8n must not receive raw private chat content unless future rights review allows it.
- Do not paste private message content into docs, tests, PRs, shell commands, logs, issue comments, n8n payloads, or CI artifacts.

## Future Cleanup Candidate

- Stale remote branches can be reviewed later for deletion only through a separate cleanup task. This audit note does not delete remote branches.
