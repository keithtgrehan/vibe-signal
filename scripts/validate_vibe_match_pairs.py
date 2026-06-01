#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "pair_id",
    "source_type",
    "text_a",
    "text_b",
    "label",
    "label_value",
    "evidence",
    "features",
    "blocked_interpretations",
    "provenance",
}
REQUIRED_FEATURES = {
    "clarity_fit",
    "boundary_fit",
    "repair_fit",
    "communication_fit",
    "pressure_risk",
    "cognitive_load_fit",
    "inconsistency_cues",
    "unsupported_claim_shift",
    "specificity_drop",
    "answer_evasion_pattern",
    "contradiction_against_prior_message",
}
ALLOWED_LABELS = {
    "communication_fit",
    "clarity_fit",
    "boundary_fit",
    "repair_fit",
    "pressure_risk",
    "cognitive_load_fit",
    "inconsistency_cues",
    "unsupported_claim_shift",
    "specificity_drop",
    "answer_evasion_pattern",
    "contradiction_against_prior_message",
}
BLOCKED_INTERPRETATIONS = ["deception", "attraction", "diagnosis", "hidden_intent"]
PRIVATE_CHAT_MARKERS = (
    "private chat",
    "real chat",
    "real ex",
    "my ex",
    "whatsapp export",
    "imessage export",
    "telegram export",
    "actual dm",
    "actual conversation",
)
COPIED_DATASET_MARKERS = (
    "copied from",
    "dataset row",
    "dailydialog",
    "daily dialog",
    "goemotions",
    "empatheticdialogues",
    "empathetic dialogues",
    "meld dataset",
)
UNSAFE_LABEL_MARKERS = (
    "deception",
    "lie",
    "lying",
    "lied",
    "attraction",
    "diagnosis",
    "hidden_intent",
    "hidden intent",
    "cheating",
    "neurotype",
    "attachment",
    "manipulation",
    "emotional_truth",
)
UNSAFE_OUTPUT_PHRASES = (
    "they lied",
    "they are lying",
    "they like you",
    "they cheated",
    "they have adhd",
    "they are autistic",
    "secretly intend",
    "attracted to you",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(row)
    return rows


def _row_label(index: int, row: dict[str, Any]) -> str:
    return f"row {index} ({row.get('pair_id', '<missing pair_id>')})"


def _contains_marker(text: str, markers: tuple[str, ...]) -> str | None:
    lowered = str(text or "").lower()
    return next((marker for marker in markers if marker in lowered), None)


def _text_payload(row: dict[str, Any]) -> str:
    evidence = row.get("evidence", [])
    evidence_text = " ".join(str(item) for item in evidence) if isinstance(evidence, list) else str(evidence)
    return " ".join([str(row.get("text_a", "")), str(row.get("text_b", "")), evidence_text])


def validate_row(row: dict[str, Any], index: int) -> list[str]:
    label = _row_label(index, row)
    errors: list[str] = []
    missing = REQUIRED_FIELDS - set(row)
    for field in sorted(missing):
        errors.append(f"{label}: missing {field}")

    if str(row.get("pair_id", "")).strip() == "":
        errors.append(f"{label}: pair_id cannot be empty")
    if row.get("source_type") != "synthetic_fixture":
        errors.append(f"{label}: source_type must be synthetic_fixture")
    if str(row.get("text_a", "")).strip() == "" or str(row.get("text_b", "")).strip() == "":
        errors.append(f"{label}: text_a and text_b must be non-empty")

    label_value = row.get("label")
    if label_value not in ALLOWED_LABELS:
        errors.append(f"{label}: unsafe label {label_value!r}")
    if _contains_marker(str(label_value), UNSAFE_LABEL_MARKERS):
        errors.append(f"{label}: unsafe label {label_value!r}")
    if row.get("label_value") not in {0, 1}:
        errors.append(f"{label}: label_value must be binary")

    evidence = row.get("evidence")
    if not isinstance(evidence, list) or not all(str(item).strip() for item in evidence):
        errors.append(f"{label}: evidence must be a non-empty list of strings")

    blocked = row.get("blocked_interpretations")
    if blocked != BLOCKED_INTERPRETATIONS:
        errors.append(f"{label}: missing blocked interpretations")

    features = row.get("features")
    if not isinstance(features, dict):
        errors.append(f"{label}: features must be an object")
    else:
        missing_features = REQUIRED_FEATURES - set(features)
        extra_features = set(features) - REQUIRED_FEATURES
        for feature in sorted(missing_features):
            errors.append(f"{label}: missing feature {feature}")
        for feature in sorted(extra_features):
            errors.append(f"{label}: unexpected feature {feature}")
        for feature, value in features.items():
            if value not in {0, 1}:
                errors.append(f"{label}: feature {feature} must be binary")

    provenance = row.get("provenance")
    if not isinstance(provenance, dict):
        errors.append(f"{label}: missing provenance")
    else:
        if provenance.get("synthetic") is not True:
            errors.append(f"{label}: provenance.synthetic must be true")
        if provenance.get("not_copied_from_real_chat") is not True:
            errors.append(f"{label}: provenance.not_copied_from_real_chat must be true")
        if str(provenance.get("created_by", "")).strip() == "":
            errors.append(f"{label}: provenance.created_by is required")

    text_payload = _text_payload(row)
    private_marker = _contains_marker(text_payload, PRIVATE_CHAT_MARKERS)
    if private_marker:
        errors.append(f"{label}: private chat marker {private_marker!r}")
    copied_marker = _contains_marker(text_payload, COPIED_DATASET_MARKERS)
    if copied_marker:
        errors.append(f"{label}: copied dataset marker {copied_marker!r}")
    unsafe_phrase = _contains_marker(text_payload, UNSAFE_OUTPUT_PHRASES)
    if unsafe_phrase:
        errors.append(f"{label}: unsafe output phrase {unsafe_phrase!r}")

    return errors


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        pair_id = str(row.get("pair_id", "")).strip()
        if pair_id in seen:
            errors.append(f"row {index} ({pair_id}): duplicate pair_id")
        seen.add(pair_id)
        errors.extend(validate_row(row, index))
    return errors


def build_summary(path: Path) -> dict[str, Any]:
    rows = load_jsonl(path)
    errors = validate_rows(rows)
    return {
        "status": "valid" if not errors else "invalid",
        "row_count": len(rows),
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate synthetic Vibe match-pair fixtures.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    try:
        summary = build_summary(Path(args.input))
    except Exception as exc:
        summary = {"status": "invalid", "row_count": 0, "errors": [str(exc)]}

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if summary["errors"]:
        print(f"Vibe match-pair validation failed: {summary['row_count']} row(s), {len(summary['errors'])} error(s).", file=sys.stderr)
        for error in summary["errors"]:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Vibe match-pair validation passed: {summary['row_count']} row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
