#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = (
    "source_id",
    "source_name",
    "source_url_or_path",
    "modality",
    "task_type",
    "license_or_terms_summary",
    "rights_tier",
    "allowed_storage",
    "allowed_commit",
    "allowed_training_use",
    "allowed_eval_use",
    "raw_body_allowed",
    "metadata_only",
    "safe_vibe_use",
    "blocked_vibe_use",
    "notes",
)

RIGHTS_TIERS = {
    "public_domain",
    "publicly_available",
    "official_public_terms_checked",
    "open_licensed",
    "licensed",
    "manual_supplied",
    "restricted",
    "synthetic_fixture",
}
ALLOWED_STORAGE_VALUES = {"metadata_only", "raw_allowed_local_only", "raw_allowed_commit", "blocked"}
ALLOWED_USE_VALUES = {"no", "review_required", "benchmark_only", "synthetic_only", "yes"}
UNSAFE_SAFE_USE_TERMS = (
    "true emotion",
    "deception",
    "diagnos",
    "attraction",
    "attachment style",
    "protected trait",
    "cheating",
    "infer neurodivergence",
)


def read_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yml", ".yaml"}:
        return yaml.safe_load(text)
    if path.suffix.lower() == ".json":
        return json.loads(text)
    raise ValueError(f"Unsupported training-source file extension: {path.suffix}")


def source_rows(payload: Any) -> list[dict[str, Any]]:
    rows = payload.get("sources") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Vibe training sources must be a list or an object with sources list.")
    return rows


def _is_external(row: dict[str, Any]) -> bool:
    return str(row.get("source_id", "")) != "synthetic_vibe_fixtures"


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and any(str(item).strip() for item in value)


def _safe_use_has_unsafe_claim(value: Any) -> bool:
    items = value if isinstance(value, list) else [value]
    text = " ".join(str(item).lower() for item in items)
    return any(term in text for term in UNSAFE_SAFE_USE_TERMS)


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        for field in REQUIRED_FIELDS:
            if field not in row:
                errors.append(f"row {index}: missing required field {field}")

        if not str(row.get("license_or_terms_summary", "")).strip():
            errors.append(f"row {index}: source lacks license/terms summary")
        if row.get("rights_tier") not in RIGHTS_TIERS:
            errors.append(f"row {index}: invalid rights_tier {row.get('rights_tier')!r}")
        if row.get("allowed_storage") not in ALLOWED_STORAGE_VALUES:
            errors.append(f"row {index}: invalid allowed_storage {row.get('allowed_storage')!r}")
        for field in ("allowed_training_use", "allowed_eval_use"):
            if row.get(field) not in ALLOWED_USE_VALUES:
                errors.append(f"row {index}: invalid {field} {row.get(field)!r}")
        for field in ("allowed_commit", "raw_body_allowed", "metadata_only"):
            if field in row and not isinstance(row.get(field), bool):
                errors.append(f"row {index}: malformed boolean {field} {row.get(field)!r}")

        raw_body_allowed = row.get("raw_body_allowed") is True
        metadata_only = row.get("metadata_only") is True
        external = _is_external(row)
        if external and raw_body_allowed:
            errors.append(f"row {index}: external research dataset cannot allow raw_body_allowed by default")
        if metadata_only and raw_body_allowed:
            errors.append(f"row {index}: metadata_only cannot also allow raw_body_allowed")
        if external and row.get("allowed_training_use") == "yes":
            notes = str(row.get("notes", "")).lower()
            if "explicit training approval" not in notes:
                errors.append(f"row {index}: training yes requires explicit approval notes")
        if not _non_empty_list(row.get("blocked_vibe_use")):
            errors.append(f"row {index}: blocked_vibe_use cannot be empty")
        if _safe_use_has_unsafe_claim(row.get("safe_vibe_use")):
            errors.append(f"row {index}: safe_vibe_use implies a disallowed claim")
    return errors


def build_summary(path: Path) -> dict[str, Any]:
    rows = source_rows(read_structured(path))
    errors = validate_rows(rows)
    return {"status": "valid" if not errors else "invalid", "row_count": len(rows), "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Vibe research/training source guardrails.")
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
        print(f"Vibe training-source validation failed: {summary['row_count']} row(s), {len(summary['errors'])} error(s).")
        for error in summary["errors"]:
            print(f"- {error}")
        return 1
    print(f"Vibe training-source validation passed: {summary['row_count']} row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
