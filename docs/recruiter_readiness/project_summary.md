# Project Summary

Vibe Signal is a privacy-conscious communication-support app that highlights observable message patterns such as clarity, ambiguity, pressure, reassurance, cognitive load, unanswered asks, boundary pressure, conflict escalation, and repair opportunities.

The project demonstrates disciplined full-stack AI product engineering under strict safety boundaries. It intentionally avoids hidden-intent, attraction, cheating, deception, diagnosis, therapy, attachment-style, neurotype, and manipulation claims.

## What Is Built

- Hosted Vite/React web app.
- Expo mobile app.
- FastAPI backend on Render.
- Deterministic cue engine with evidence objects and safe output contracts.
- `/api/analyze`, `/api/match`, `/api/feedback`, legal routes, `/healthz`, and `/api/status`.
- Consent-gated private-input flow and synthetic demo-first experience.
- Public-copy, no-raw-content, and restricted-artifact safety scanners.
- Dataset rights registry and commercial fail-closed validation.
- 10k synthetic split-aware evaluation harness with dev, hard-negative, held-out, and red-team splits.
- Human-review packet scaffolding for future observable-cue labeling.

## Evaluation Story

The current evaluation story is intentionally narrow:

- Synthetic regression checks prove contract coverage, not real-world accuracy.
- Bootstrap cue labels come from fixture expectations, not human reviewers.
- Hard-negative and red-team sets test false-positive and safety behavior under synthetic conditions.
- Human-reviewed labels are pending before any validation or model-quality claim.

PR #29 reports the latest local synthetic regression hardening:

- evidence completeness `5000/5000`
- unsafe-output block `5000/5000`
- red-team safety `500/500`
- hard-negative unexpected cues reduced from `334` to `0`
- bootstrap-only micro P/R/F1 improved to `0.6646 / 0.947 / 0.7811`

These are not accuracy claims.

## Why It Is Recruiter-Relevant

This repo shows:

- end-to-end product delivery across web, mobile, and backend
- deterministic NLP design with explicit evidence and limits
- safety-conscious product positioning
- evaluation harness design beyond toy unit tests
- privacy and data-rights judgment
- careful closed-beta readiness discipline
- honest documentation of blockers and non-claims

## Remaining Gaps

- Real-device iPhone/TestFlight QA is pending.
- Legal/privacy review is pending.
- Human-reviewed labels are pending.
- Deployed backend commit proof depends on Render metadata env vars.
- Tester invites remain blocked until P0 gates pass.

