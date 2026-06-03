# Public-Copy Safety Audit

Date: 2026-06-03.

Status: `PASS_WITH_ALLOWLISTED_INTERNAL_REFERENCES`.

## Scanner

Command:

```bash
python scripts/check_public_copy_safety.py
```

Result:

- Configured public surfaces scanned.
- Unsafe public-copy findings: `0`.
- Internal/boundary references are allowlisted in `configs/public_copy_safety_allowlist.yml` with path-level reasons.

## Public Surfaces Covered

- `README.md`
- `web/src/App.tsx`
- `web/src/api.js`
- `web/index.html`
- `web/public/opengraph.svg`
- `mobile/src/App.js`
- `mobile/src/screens/*.js`
- `backend/routes/analyze.py`
- `backend/routes/legal.py`
- tester/legal/privacy/support docs listed in the scanner

## Blocked Public Claims

The scanner rejects public/user-visible uses of hidden-motive, attraction, deception, diagnosis, identity-label, coercive influence, guarantee, and relationship-truth claims.

## Allowlist Rules

Allowed internal mentions are restricted to:

- blocked-term registries
- safety tests
- red-line docs
- research/source-register docs
- generated evaluation metadata
- proof docs that explicitly describe what is blocked

The allowlist is not legal approval and must not be used for consumer UI, beta signup copy, app metadata, or public marketing claims.
