# Data Deletion Request Draft

Status: draft for closed-beta readiness only. This document is not legal advice, does not claim production compliance, and requires legal review before public launch.

## Current Scope

The local backend does not persist raw messages by default for `/api/analyze` or `/api/match`.

Deletion requests are expected to cover stored metadata only when those systems are enabled, such as:

- consented feedback metadata
- event metadata
- device-scoped identifiers
- billing or entitlement metadata handled by a configured provider
- support records created through a future support channel

## What To Include

A deletion request should include:

- contact email or support contact method
- approximate submission date
- the route or feature used, if known
- non-sensitive identifiers such as feedback ID, event ID, device-scoped app user ID, or receipt reference when available

## What Not To Include

Do not include:

- raw chat text
- sensitive personal data
- secrets, passwords, tokens, or API keys
- medical data
- legal documents
- financial data
- unrelated third-party private messages

## Draft Handling Workflow

1. Confirm the requester has supplied enough non-sensitive information to search stored metadata.
2. Locate consented feedback, event metadata, device-scoped identifiers, billing references, or support records.
3. Delete or anonymize matching records according to the reviewed retention policy.
4. Record only minimal request-handling metadata required by the reviewed policy.
5. Reply through the reviewed support channel after legal-approved identity and response checks.

## Closed-Beta Limits

Closed beta is not production launch. Final deletion endpoint, support contact, identity check, retention window, and response timeline are future work and require legal review before public launch.
