# UI Feedback To Human Label Review

Date: 2026-06-04

## Purpose

The web UI can collect bounded feedback metadata to help prioritize future human review. This metadata is not a human-reviewed label and must not be treated as evaluation truth.

## Metadata Allowed

- `result_id` / match id
- selected feedback label
- visible cue id or pattern id
- evidence quality label
- selected goal
- selected context
- selected analysis style
- low-signal flag
- synthetic/demo flag
- client event id and timestamp

## Metadata Not Allowed

- pasted message text
- evidence quote text
- draft reply text
- names, phone numbers, emails, links, or handles
- free-form comments in the standard feedback row

## Review Use

Feedback can help choose which results deserve human review first. Reviewers still label observable wording only, verify evidence spans independently, and keep manual gates human.

## Product Boundary

Cue feedback such as "This cue fits," "Too strong," or "Wrong cue" is a user signal for review prioritization. It does not become a training label, product accuracy claim, or release gate by itself.
