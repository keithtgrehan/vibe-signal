# Open PR Debt Triage

Date: 2026-06-06

Status: read-only triage report. No pull requests were merged, closed, or modified by this report.

## Summary

The open PR queue contains one current acceleration PR and six older PRs from earlier Replit, A/B, and private-data/model-workflow experiments. The older PRs create strategic drag because several are now superseded by the Scanner redesign, static-first legal pages, Vercel/Render production architecture, and private metadata guardrails.

Recommended operating rule: do not merge stale PRs wholesale. Merge only narrow, green, current work. Close superseded frontend/A/B PRs after human confirmation. For private WhatsApp/model-workflow PRs, extract only safe deterministic or synthetic ideas into new branches after the current private metadata guard scans pass.

## Current Open PRs

| PR | Branch | Status observed | Files touched | Classification | Recommendation |
| --- | --- | --- | --- | --- | --- |
| [#61](https://github.com/keithtgrehan/vibe-signal/pull/61) Add local-only private gold label evaluator scaffold | `codex/local-gold-label-evaluator-scaffold` | `CLEAN`; checks green when last inspected | Local-only evaluator tools, tests, model-training plan doc | merge as-is | Merge after normal review. It adds aggregate-only validation/evaluation scaffolding and does not train a model or commit private data. |
| [#40](https://github.com/keithtgrehan/vibe-signal/pull/40) Document minimal UI merge and Replit A/B plan | `docs/minimal-ui-merge-proof` | `UNKNOWN`; docs-only | Replit A/B and minimal UI proof docs | close as superseded | Superseded by Scanner redesign, custom-domain production docs, and no-render deployment hardening. Keep only if Keith wants historical archive docs. |
| [#41](https://github.com/keithtgrehan/vibe-signal/pull/41) Document UI A/B variant governance | `docs/ab-test-variant-governance` | `UNKNOWN`; docs-only | A/B governance docs | cherry-pick safe parts | Potentially useful for future experiment governance, but should be reconciled with the current no-analytics/no-tracking posture before merge. Do not imply active A/B testing infrastructure. |
| [#42](https://github.com/keithtgrehan/vibe-signal/pull/42) Replit A/B frontend experiment | `replit/ab-minimal-frontend-redesign` | draft; `UNKNOWN` | Web UI, variants, API config, safety scanner | close as superseded | Superseded by the production Scanner redesign and custom-domain API-base fixes. Do not merge over current web UI. |
| [#44](https://github.com/keithtgrehan/vibe-signal/pull/44) Improve private WhatsApp cue-labeling and weak-label engine workflow | `codex/private-whatsapp-engine-improvement-nightly` | `DIRTY` | Private-inspired data/tooling, weak-label training script, reports, taxonomy, tests | blocked due to private-data/model-risk | Do not merge wholesale. Extract only safe deterministic cue taxonomy improvements or synthetic fixture ideas into fresh branches after private metadata guard scans. No training script merge until evaluator gates and human review approve it. |
| [#45](https://github.com/keithtgrehan/vibe-signal/pull/45) Allow exact Replit A/B origin for CORS | `codex/allow-replit-ab-cors` | `DIRTY` | Backend deployment env example, Replit CORS proof, deployment readiness test | needs human review | Likely superseded by Vercel/Render custom-domain CORS setup unless a live Replit preview remains active. Do not merge if it conflicts with current production allowed origins. |
| [#46](https://github.com/keithtgrehan/vibe-signal/pull/46) Add safe WhatsApp dynamics research prototype | `codex/whatsapp-dynamics-research-prototype` | draft; `DIRTY` | Private dynamics tooling, model scripts, synthetic fixtures, web variants, safety scripts | blocked due to private-data/model-risk | Do not merge wholesale. It overlaps with #42 and #44 and includes model/prototype workflow files. Extract safe research notes or synthetic-only hard-negative ideas into new PRs after guard scans. |

## Suggested Next Actions

1. Merge #61 first after human review, because it is current, green, and directly supports the approved Phase 1 evaluator path.
2. Close #42 as superseded by the Scanner redesign and current Vercel/Render architecture.
3. Close #40 unless Keith wants to preserve the older Replit/minimal UI proof docs as historical context.
4. Review #41 manually for any governance language worth moving into current docs, with no analytics/tracking assumptions.
5. Review #45 only if Replit preview support is still needed; otherwise close as superseded by production custom-domain CORS work.
6. Treat #44 and #46 as extract-only source material. Do not merge training scripts, private-inspired reports, or private dynamics workflow wholesale.
7. For any extracted idea from #44/#46, open a fresh PR from current `main`, run `python scripts/check_private_metadata_exposure.py`, and keep production deterministic until evaluator gates prove value.

## Guardrails For Closing Or Extracting

- Do not merge private WhatsApp/model workflow PRs wholesale.
- Do not train a model from private rows.
- Do not commit private CSV/XLSX/ZIP/JSONL/model/report artifacts.
- Do not expose private source identifiers or real-person-derived metadata.
- Do not add public datasets or dataset downloads.
- Do not weaken public-copy, private-metadata, no-raw-content, or restricted-artifact checks.
- Do not add analytics, cookies, tracking, storage, providers, account systems, or payment flows while resolving PR debt.
- Keep n8n as operations/workflow automation only, not the AI engine and not a raw private-chat processor.

## Notes

This report is intentionally conservative. Green checks on an older branch are not enough to merge if the product direction, legal posture, privacy guardrails, or production architecture have changed since that branch was opened.
