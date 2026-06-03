# Synthetic Data

This directory contains hand-authored synthetic fixtures for deterministic regression and evaluation scaffolding.

It does not contain real user chats, tester messages, private conversations, scraped messages, or raw external datasets.

## Current Fixture Set

- [whatsapp/](whatsapp/): synthetic WhatsApp-style conversations used by the engine regression harness.
- Split manifest: [whatsapp/fixture_manifest.json](whatsapp/fixture_manifest.json)
- Split docs: [whatsapp/README.md](whatsapp/README.md)

## Intended Use

- synthetic regression
- cue contract checks
- evidence completeness checks
- hard-negative false-positive checks
- red-team safety checks
- bootstrap-only human-review packet seeding

## Non-Claims

- Synthetic fixtures are not real-world validation.
- Bootstrap labels are not human-reviewed labels.
- Reports generated from these fixtures are not accuracy, model-quality, or production-readiness claims.
- Private evaluation labels must never become product capabilities.

