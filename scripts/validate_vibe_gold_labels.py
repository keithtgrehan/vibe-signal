#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "conversation_id",
    "label_id",
    "label_type",
    "direction",
    "speaker_role",
    "evidence_text",
    "evidence_start",
    "evidence_end",
    "confidence",
    "reviewer",
    "notes",
)

ENUMS = {
    "label_type": {
        "clarity_issue",
        "hedging_shift",
        "specificity_shift",
        "directness_shift",
        "reassurance_request",
        "pressure_language",
        "boundary_violation",
        "repair_attempt",
        "topic_shift",
        "potential_overload",
        "neutral",
    },
    "direction": {"increased", "decreased", "mixed", "present", "absent", "neutral", "unknown"},
    "speaker_role": {"self", "other", "interviewer", "candidate", "unknown"},
    "confidence": {"low", "medium", "high"},
}

UNSAFE_FIELDS = {
    "emotion_label",
    "deception_score",
    "attraction_score",
    "attachment_style",
    "diagnosis",
    "manipulation_score",
    "protected_trait_inference",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() != ".jsonl":
        raise ValueError("Vibe gold labels must be JSONL.")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"line {line_number}: every row must be an object")
            rows.append(row)
    return rows


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen_label_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        for field in REQUIRED_FIELDS:
            if field not in row:
                errors.append(f"row {index}: missing required field {field}")
        for field in UNSAFE_FIELDS:
            if field in row:
                errors.append(f"row {index}: unsafe field {field} is not allowed")

        label_id = str(row.get("label_id", "")).strip()
        if not label_id:
            errors.append(f"row {index}: label_id is required")
        elif label_id in seen_label_ids:
            errors.append(f"row {index}: duplicate label_id {label_id!r}")
        seen_label_ids.add(label_id)

        for field, allowed in ENUMS.items():
            if field in row and row.get(field) not in allowed:
                errors.append(f"row {index}: invalid {field} {row.get(field)!r}")

        if row.get("label_type") != "neutral" and not str(row.get("evidence_text", "")).strip():
            errors.append(f"row {index}: evidence_text is required for non-neutral labels")

        start = row.get("evidence_start")
        end = row.get("evidence_end")
        if not isinstance(start, int) or start < 0:
            errors.append(f"row {index}: evidence_start must be an integer >= 0")
        if not isinstance(end, int) or end < 0:
            errors.append(f"row {index}: evidence_end must be an integer >= 0")
        if isinstance(start, int) and isinstance(end, int) and end < start:
            errors.append(f"row {index}: evidence_end must be >= evidence_start")
    return errors


def build_summary(path: Path) -> dict[str, Any]:
    rows = load_jsonl(path)
    errors = validate_rows(rows)
    return {"status": "valid" if not errors else "invalid", "row_count": len(rows), "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Vibe gold-label JSONL.")
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
        print(f"Vibe gold-label validation failed: {summary['row_count']} row(s), {len(summary['errors'])} error(s).")
        for error in summary["errors"]:
            print(f"- {error}")
        return 1
    print(f"Vibe gold-label validation passed: {summary['row_count']} row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
