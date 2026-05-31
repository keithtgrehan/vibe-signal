#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = (
    "claim_id",
    "claim_text",
    "status",
    "evidence_required",
    "allowed_surface",
    "blocked_reason",
    "notes",
)

ALLOWED_STATUS = {"supported", "gated", "blocked"}
BLOCKED_SUPPORTED_TERMS = (
    "deception",
    "hidden intent",
    "true emotion",
    "lying",
    "cheating",
    "diagnosis",
    "mental health judgment",
    "relationship outcome",
    "hiring outcome",
    "emotion recognition",
    "biometric",
    "manipulation score",
    "production model",
)


def read_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yml", ".yaml"}:
        return yaml.safe_load(text)
    if path.suffix.lower() == ".json":
        return json.loads(text)
    raise ValueError(f"Unsupported claims matrix file extension: {path.suffix}")


def claim_rows(payload: Any) -> list[dict[str, Any]]:
    rows = payload.get("claims") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Claims matrix must be a list or an object with claims list.")
    return rows


def _contains_blocked_supported_term(text: str) -> str | None:
    lowered = str(text or "").lower()
    for term in BLOCKED_SUPPORTED_TERMS:
        if term in lowered:
            return term
    return None


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        for field in REQUIRED_FIELDS:
            if field not in row:
                errors.append(f"row {index}: missing required field {field}")

        claim_id = str(row.get("claim_id", "")).strip()
        if not claim_id:
            errors.append(f"row {index}: claim_id is required")
        elif claim_id in seen:
            errors.append(f"row {index}: duplicate claim_id {claim_id!r}")
        seen.add(claim_id)

        status = row.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"row {index}: invalid status {status!r}")

        if "evidence_required" in row and not isinstance(row.get("evidence_required"), bool):
            errors.append(f"row {index}: evidence_required must be boolean")

        text = " ".join(str(row.get(field, "")) for field in ("claim_text", "notes"))
        blocked_term = _contains_blocked_supported_term(text)
        if status in {"supported", "gated"} and blocked_term:
            errors.append(f"row {index}: supported/gated claim contains disallowed term {blocked_term!r}")

        if status == "supported" and "statistical significance" in text.lower():
            errors.append(f"row {index}: statistical-significance language is not supported")
        if status == "gated" and "statistical significance" in text.lower():
            if row.get("statistical_significance_allowed") is not True:
                errors.append(f"row {index}: statistical-significance language requires explicit gate")

        if status == "blocked" and not str(row.get("blocked_reason", "")).strip():
            errors.append(f"row {index}: blocked claim requires blocked_reason")
    return errors


def build_summary(path: Path) -> dict[str, Any]:
    rows = claim_rows(read_structured(path))
    errors = validate_rows(rows)
    return {"status": "valid" if not errors else "invalid", "row_count": len(rows), "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Vibe claims matrix guardrails.")
    parser.add_argument("--path", required=True)
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    try:
        summary = build_summary(Path(args.path))
    except Exception as exc:
        summary = {"status": "invalid", "row_count": 0, "errors": [str(exc)]}

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if summary["errors"]:
        print(f"Vibe claims matrix validation failed: {summary['row_count']} row(s), {len(summary['errors'])} error(s).")
        for error in summary["errors"]:
            print(f"- {error}")
        return 1
    print(f"Vibe claims matrix validation passed: {summary['row_count']} row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
