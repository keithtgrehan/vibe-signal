#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = (
    "source_id",
    "source_name",
    "source_url_or_path",
    "source_type",
    "rights_tier",
    "license_or_terms_summary",
    "allowed_storage",
    "allowed_commit",
    "allowed_training_use",
    "allowed_eval_use",
    "raw_body_allowed",
    "metadata_only",
    "acquisition_method",
    "paywall_or_login_status",
    "robots_status",
    "provenance_hash",
    "last_checked_at",
    "reviewer_or_operator",
    "blocked_reason",
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
SOURCE_TYPES = {
    "user_owned_chat",
    "user_supplied_text",
    "pasted_chat",
    "whatsapp_export",
    "manual_local",
    "synthetic_fixture",
    "platform_export_metadata",
    "platform_url_metadata",
    "research_dataset",
    "licensed_dataset",
    "restricted_external_dataset",
    "benchmark_dataset",
    "audio_metadata",
    "video_metadata",
    "provider_metadata",
    "provider_response_metadata",
    "blocked_reference",
}
ALLOWED_STORAGE_VALUES = {"metadata_only", "raw_allowed_local_only", "raw_allowed_commit", "blocked"}
ALLOWED_USE_VALUES = {"no", "review_required", "benchmark_only", "synthetic_only", "yes"}
PLACEHOLDER_VALUES = {"", "pending", "todo", "tbd", "unknown", "n/a"}
ALIAS_FIELDS = (
    ("allowed_commit", "commit_allowed"),
    ("allowed_training_use", "training_allowed"),
    ("allowed_eval_use", "eval_allowed"),
)


def read_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yml", ".yaml"}:
        return yaml.safe_load(text)
    if path.suffix.lower() == ".json":
        return json.loads(text)
    raise ValueError(f"Unsupported registry file extension: {path.suffix}")


def resource_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = payload.get("resources")
    else:
        rows = None
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Vibe resource registry must be a list or an object with a resources list.")
    return rows


def normalize_aliases(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    for primary, alias in ALIAS_FIELDS:
        if primary not in normalized and alias in normalized:
            normalized[primary] = normalized[alias]
    return normalized


def stable_provenance_hash(row: dict[str, Any]) -> str:
    payload = {
        "source_id": str(row.get("source_id", "")),
        "source_name": str(row.get("source_name", "")),
        "source_url_or_path": str(row.get("source_url_or_path", "")),
        "source_type": str(row.get("source_type", "")),
        "rights_tier": str(row.get("rights_tier", "")),
        "license_or_terms_summary": str(row.get("license_or_terms_summary", "")),
        "last_checked_at": str(row.get("last_checked_at", "")),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _is_real_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _placeholder(value: Any) -> bool:
    return str(value or "").strip().lower() in PLACEHOLDER_VALUES


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, original_row in enumerate(rows, start=1):
        row = normalize_aliases(original_row)
        for field in REQUIRED_FIELDS:
            if field not in row:
                errors.append(f"row {index}: missing required field {field}")

        source_id = str(row.get("source_id", "")).strip()
        if not source_id:
            errors.append(f"row {index}: source_id is required")
        elif source_id in seen:
            errors.append(f"row {index}: duplicate source_id {source_id!r}")
        seen.add(source_id)

        rights_tier = str(row.get("rights_tier", "")).strip()
        source_type = str(row.get("source_type", "")).strip()
        allowed_storage = str(row.get("allowed_storage", "")).strip()
        training_use = str(row.get("allowed_training_use", "")).strip()
        eval_use = str(row.get("allowed_eval_use", "")).strip()

        if rights_tier not in RIGHTS_TIERS:
            errors.append(f"row {index}: invalid rights_tier {rights_tier!r}")
        if source_type not in SOURCE_TYPES:
            errors.append(f"row {index}: invalid source_type {source_type!r}")
        if allowed_storage not in ALLOWED_STORAGE_VALUES:
            errors.append(f"row {index}: invalid allowed_storage {allowed_storage!r}")
        if training_use not in ALLOWED_USE_VALUES:
            errors.append(f"row {index}: invalid allowed_training_use {training_use!r}")
        if eval_use not in ALLOWED_USE_VALUES:
            errors.append(f"row {index}: invalid allowed_eval_use {eval_use!r}")

        for field in ("allowed_commit", "raw_body_allowed", "metadata_only"):
            if field in row and not _is_real_bool(row.get(field)):
                errors.append(f"row {index}: malformed boolean {field} {row.get(field)!r}")

        allowed_commit = row.get("allowed_commit") is True
        raw_body_allowed = row.get("raw_body_allowed") is True
        metadata_only = row.get("metadata_only") is True

        license_summary = str(row.get("license_or_terms_summary", "")).strip()
        if _placeholder(license_summary):
            errors.append(f"row {index}: license_or_terms_summary is required")

        provenance_hash = str(row.get("provenance_hash", "")).strip()
        if _placeholder(provenance_hash) or not provenance_hash.startswith("sha256:"):
            errors.append(f"row {index}: provenance_hash must be populated and start with sha256:")

        restricted = rights_tier == "restricted" or source_type in {"blocked_reference", "restricted_external_dataset"}
        if restricted and raw_body_allowed:
            errors.append(f"row {index}: restricted source cannot allow raw_body_allowed")
        if restricted and (allowed_commit or allowed_storage == "raw_allowed_commit"):
            errors.append(f"row {index}: restricted source cannot allow commit")
        if restricted and (training_use != "no" or eval_use != "no"):
            errors.append(f"row {index}: restricted source cannot allow training/eval")
        if metadata_only and raw_body_allowed:
            errors.append(f"row {index}: metadata_only cannot also allow raw_body_allowed")
        if raw_body_allowed and _placeholder(license_summary):
            errors.append(f"row {index}: raw_body_allowed requires explicit terms/rights notes")
        if raw_body_allowed and not any(
            token in license_summary.lower() for token in ("rights", "terms", "license", "consent", "synthetic")
        ):
            errors.append(f"row {index}: raw_body_allowed requires explicit terms/rights notes")
    return errors


def build_summary(path: Path) -> dict[str, Any]:
    rows = resource_rows(read_structured(path))
    errors = validate_rows(rows)
    return {"status": "valid" if not errors else "invalid", "row_count": len(rows), "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Vibe Engine resource registry rights guardrails.")
    parser.add_argument("--path", required=True, help="YAML or JSON registry path.")
    parser.add_argument("--json-out", help="Optional machine-readable validation summary.")
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
        print(f"Vibe resource registry validation failed: {summary['row_count']} row(s), {len(summary['errors'])} error(s).")
        for error in summary["errors"]:
            print(f"- {error}")
        return 1
    print(f"Vibe resource registry validation passed: {summary['row_count']} row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
