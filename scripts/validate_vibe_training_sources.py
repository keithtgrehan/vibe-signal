#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = (
    "source_id",
    "name",
    "modality",
    "task",
    "license_name",
    "license_url",
    "download_method",
    "access_notes",
    "training_use_allowed",
    "commercial_use_allowed",
    "research_only",
    "rights_tier",
    "safe_vibe_use",
    "blocked_vibe_use",
    "registry_status",
    "notes",
)
BOOL_FIELDS = ("training_use_allowed", "commercial_use_allowed", "research_only")
RIGHTS_TIERS = {"open", "NC", "manual-review", "restricted", "eval-only", "unknown"}
PROJECT_MODES = {"research_only", "commercial"}
COMMERCIAL_BLOCKED_TIERS = {"NC", "manual-review", "restricted", "eval-only", "unknown"}
NON_TRAINING_TIERS = {"manual-review", "restricted", "eval-only", "unknown"}
UNKNOWN_MARKERS = ("unknown", "ambiguous", "tbd", "to be determined")
UNSAFE_SAFE_USE_TERMS = (
    "true emotion",
    "deception",
    "diagnos",
    "attraction",
    "attachment style",
    "protected trait",
    "cheating",
    "infer neurodivergence",
    "infer neurotype",
    "neurotype inference",
    "manipulation",
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
        raise ValueError("Vibe training sources must be a list or an object with a sources list.")
    return rows


def _row_label(index: int, row: dict[str, Any]) -> str:
    source_id = str(row.get("source_id") or "<missing source_id>")
    return f"row {index} ({source_id})"


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and any(str(item).strip() for item in value)


def _has_unknown_marker(value: Any) -> bool:
    text = str(value or "").strip().lower()
    if not text:
        return True
    return any(marker == text or marker in text for marker in UNKNOWN_MARKERS)


def _safe_use_has_unsafe_claim(value: Any) -> bool:
    items = value if isinstance(value, list) else [value]
    text = " ".join(str(item).lower() for item in items)
    return any(term in text for term in UNSAFE_SAFE_USE_TERMS)


def _is_research_only_usage(row: dict[str, Any]) -> bool:
    usage = str(row.get("usage", "")).strip().lower().replace("-", "_")
    return usage == "research_only"


def is_research_training_ready(row: dict[str, Any]) -> bool:
    return (
        row.get("training_use_allowed") is True
        and row.get("research_only") is True
        and row.get("commercial_use_allowed") is False
        and row.get("rights_tier") == "NC"
        and _is_research_only_usage(row)
    )


def validate_rows(rows: list[dict[str, Any]], project_mode: str) -> list[str]:
    if project_mode not in PROJECT_MODES:
        return [f"invalid project mode {project_mode!r}"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        label = _row_label(index, row)
        missing_fields = [field for field in REQUIRED_FIELDS if field not in row]
        for field in missing_fields:
            errors.append(f"{label}: missing required field {field}")
        if missing_fields:
            continue

        source_id = str(row.get("source_id", "")).strip()
        if not source_id:
            errors.append(f"{label}: source_id cannot be empty")
        elif source_id in seen_ids:
            errors.append(f"{label}: duplicate source_id {source_id}")
        seen_ids.add(source_id)

        for field in REQUIRED_FIELDS:
            value = row.get(field)
            if field in {"safe_vibe_use", "blocked_vibe_use"}:
                if not _non_empty_list(value):
                    errors.append(f"{label}: {field} must be a non-empty list")
            elif isinstance(value, str) and not value.strip():
                errors.append(f"{label}: {field} cannot be empty")

        for field in BOOL_FIELDS:
            if not isinstance(row.get(field), bool):
                errors.append(f"{label}: {field} must be true or false")

        rights_tier = row.get("rights_tier")
        if rights_tier not in RIGHTS_TIERS:
            errors.append(f"{label}: invalid rights_tier {rights_tier!r}")
        if rights_tier == "unknown":
            errors.append(f"{label}: unknown or ambiguous rights fail closed")
        if _has_unknown_marker(row.get("license_name")):
            errors.append(f"{label}: unknown or ambiguous license_name fails closed")
        if _has_unknown_marker(row.get("license_url")):
            errors.append(f"{label}: unknown or ambiguous license_url fails closed")

        if _safe_use_has_unsafe_claim(row.get("safe_vibe_use")):
            errors.append(f"{label}: safe_vibe_use implies a disallowed claim")

        training_allowed = row.get("training_use_allowed") is True
        research_only = row.get("research_only") is True
        if training_allowed and rights_tier in NON_TRAINING_TIERS:
            errors.append(f"{label}: {rights_tier} source cannot be training-ready")
        if training_allowed and rights_tier == "NC":
            if not research_only:
                errors.append(f"{label}: NC training source must be marked research_only=true")
            if not _is_research_only_usage(row):
                errors.append(f"{label}: NC training source must declare usage=research_only")
        if not training_allowed and str(row.get("registry_status", "")).endswith("training_allowed"):
            errors.append(f"{label}: registry_status cannot mark non-training source as training_allowed")

        if project_mode == "commercial":
            if row.get("commercial_use_allowed") is not True:
                errors.append(f"{label}: commercial mode rejects source because commercial_use_allowed must be true")
            if row.get("training_use_allowed") is not True:
                errors.append(f"{label}: commercial mode rejects source because training_use_allowed must be true")
            if row.get("research_only") is True:
                errors.append(f"{label}: commercial mode rejects research-only source")
            if rights_tier in COMMERCIAL_BLOCKED_TIERS:
                errors.append(f"{label}: commercial mode rejects rights_tier {rights_tier}")

    return errors


def build_summary(path: Path, project_mode: str) -> dict[str, Any]:
    rows = source_rows(read_structured(path))
    errors = validate_rows(rows, project_mode)
    return {
        "status": "valid" if not errors else "invalid",
        "project_mode": project_mode,
        "row_count": len(rows),
        "training_ready_source_ids": [row["source_id"] for row in rows if is_research_training_ready(row)],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Vibe training-source rights gates.")
    config_group = parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument("--config", dest="config")
    config_group.add_argument("--path", dest="config", help=argparse.SUPPRESS)
    parser.add_argument("--project-mode", choices=sorted(PROJECT_MODES), default="research_only")
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    try:
        summary = build_summary(Path(args.config), args.project_mode)
    except Exception as exc:
        summary = {"status": "invalid", "project_mode": args.project_mode, "row_count": 0, "training_ready_source_ids": [], "errors": [str(exc)]}

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if summary["errors"]:
        print(
            f"Vibe training-source validation failed: {summary['row_count']} row(s), "
            f"{len(summary['errors'])} error(s), project_mode={summary['project_mode']}."
        )
        for error in summary["errors"]:
            print(f"- {error}")
        return 1
    print(
        f"Vibe training-source validation passed: {summary['row_count']} row(s), "
        f"{len(summary['training_ready_source_ids'])} research training-ready source(s), "
        f"project_mode={summary['project_mode']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
