# Private WhatsApp Training Plan

## Purpose

This plan defines a local-only path for ingesting a consent-backed private WhatsApp export, redacting it, preparing human cue-label review rows, and evaluating reviewed labels in aggregate. The goal is future cue-model research, not product inference or runtime behavior changes.

## Consent Assumptions

- The source is used only when the user asserts that every relevant participant has consented to local research review.
- Consent records stay outside the model and outside committed artifacts.
- Consent can be withdrawn. Withdrawal requires deleting raw and derived private files.
- Commercial or product training is not allowed unless separately approved and documented.

## Restrictions

- Do not commit raw exports, raw chat text, parsed private messages, participant names, or review files containing private text.
- Do not send the data to third-party APIs.
- Do not train a production model from this source in this phase.
- Do not change backend or frontend behavior.
- Keep all generated files under `data/restricted/private_whatsapp/`.
- Treat redacted examples as restricted unless separately reviewed and approved.

## Allowed Labels

Allowed labels are observable communication cues only:

- `ambiguity`
- `unclear_timing`
- `direct_ask`
- `unanswered_ask_candidate`
- `pressure_urgency`
- `boundary`
- `reassurance`
- `repair_attempt`
- `escalation_risk`

## Blocked Labels

Blocked labels include claims about hidden or unsupported states:

- hidden intent or motive
- attraction or romantic interest
- deception, lying, or cheating
- diagnosis, neurotype, personality, or attachment style
- emotional truth or true feelings
- manipulation scoring or persuasion optimization
- relationship prediction, dating score, or outcome prediction

## Ingestion Process

1. Place the WhatsApp export zip outside git or under `data/restricted/private_whatsapp/`.
2. Run `tools/ingest_private_whatsapp.py --zip-path <path-to-export.zip>`.
3. The tool parses `_chat.txt` rows in `[DD.MM.YY, HH:MM:SS] Sender: Message` format.
4. Multiline messages are attached to the prior message.
5. Sender names are converted to `speaker_role`: `self` for the first parsed sender or explicit `self`, and `other` for everyone else.
6. The tool writes local-only message and stats outputs under the restricted folder.
7. The tool prints only aggregate status and role counts.

## Redaction Process

1. Run `tools/redact_private_whatsapp.py` on the restricted JSONL.
2. Redaction replaces obvious names, emails, phone numbers, URLs, and dates/times by default.
3. The redacted JSONL preserves `message_id` and `speaker_role`.
4. Redacted files remain restricted/local and are not commit-ready by default.
5. The tool prints only aggregate redaction counts.

## Label Review Process

1. Run `tools/prepare_private_label_review.py` on the restricted redacted JSONL.
2. The tool creates one-to-three-turn windows.
3. Weak candidate labels come from deterministic keyword rules and are only prompts for human review.
4. A human reviewer fills `review_label`, `severity`, `safe_next_step`, and `reviewer_notes`.
5. Reviewers must label visible wording only and leave low-signal rows blank or noted as low signal.
6. Review CSV files remain restricted/local.

## Model Training Plan

- No model is trained in this phase.
- Future training requires human-reviewed labels, deletion handling, source-rights review, and explicit approval.
- Training must use only allowed observable cue labels.
- Any candidate model must be evaluated against synthetic, hard-negative, red-team, and human-reviewed cue sets before consideration.
- Production use requires a separate gated decision and updated model card.

## Promotion Criteria

Promotion out of local research requires:

- documented consent and deletion procedure coverage
- no raw or redacted private text in git
- human-reviewed labels with reviewer notes
- aggregate evaluation reports only
- safety review for blocked-label leakage
- privacy review for storage, export, and deletion flows
- no regression in backend, frontend, or existing safety gates

## Deletion And Export Process

- Deletion request: remove the source zip, parsed JSONL, redacted JSONL, review CSVs, aggregate reports, local caches, and any derived training files from the restricted folder.
- Export request: provide only the locally held files that are approved for export by the consent process. Do not expose other participants' data without appropriate consent review.
- Document deletion/export completion outside committed artifacts.

## No Production Claims

This pipeline does not prove model quality, real-world accuracy, production readiness, or relationship outcomes. It supports local cue review and future research only.
