#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from tools.private_gold_label_utils import (
    ALLOWED_LABELS,
    EVIDENCE_COLUMNS,
    GOLD_LABEL_COLUMNS,
    KNOWN_COLUMNS,
    LOW_SIGNAL_LABELS,
    REJECT_LABELS,
    REVIEW_STATUS_COLUMNS,
    ROW_ID_COLUMNS,
    SAFE_NEXT_STEP_COLUMNS,
    SEVERITY_COLUMNS,
    PrivateGoldLabelError,
    categorize_safe_next_step,
    first_present,
    has_any_value,
    read_table,
    safe_counter,
    split_labels,
    normalize_severity,
    RESTRICTED_ROOT,
)


def validate_file(path: Path, *, file_format: str | None = None, restricted_root: Path = RESTRICTED_ROOT) -> dict[str, Any]:
    fieldnames, rows = read_table(path, file_format=file_format, restricted_root=restricted_root)
    return build_summary(fieldnames, rows)


def build_summary(fieldnames: list[str], rows: list[dict[str, str]]) -> dict[str, Any]:
    row_id_column = first_present(fieldnames, ROW_ID_COLUMNS)
    gold_label_column = first_present(fieldnames, GOLD_LABEL_COLUMNS)
    status_column = first_present(fieldnames, REVIEW_STATUS_COLUMNS)
    severity_column = first_present(fieldnames, SEVERITY_COLUMNS)
    safe_next_step_column = first_present(fieldnames, SAFE_NEXT_STEP_COLUMNS)
    evidence_columns = [field for field in fieldnames if field.lower() in EVIDENCE_COLUMNS]

    missing_required_columns: list[str] = []
    if row_id_column is None:
        missing_required_columns.append("row_id")
    if gold_label_column is None:
        missing_required_columns.append("gold_label")

    unknown_column_count = sum(1 for field in fieldnames if field.lower() not in KNOWN_COLUMNS)
    severity_distribution: Counter[str] = Counter()
    cue_distribution: Counter[str] = Counter()
    safe_next_step_distribution: Counter[str] = Counter()
    missing_required_values = 0
    reviewed_rows = 0
    rejected_rows = 0
    low_signal_rows = 0
    invalid_label_rows = 0
    missing_evidence_span_count = 0

    for row in rows:
        if row_id_column is not None and not str(row.get(row_id_column, "")).strip():
            missing_required_values += 1
        raw_gold = str(row.get(gold_label_column, "") if gold_label_column else "")
        labels = split_labels(raw_gold)
        if gold_label_column is not None and not labels:
            missing_required_values += 1
        if not labels:
            continue

        reviewed_rows += 1
        invalid_labels = [label for label in labels if label not in ALLOWED_LABELS]
        if invalid_labels:
            invalid_label_rows += 1
            continue

        cue_distribution.update(labels)
        status_value = str(row.get(status_column, "") if status_column else "").strip().lower()
        if status_value in REJECT_LABELS or any(label in REJECT_LABELS for label in labels):
            rejected_rows += 1
        if status_value in LOW_SIGNAL_LABELS or any(label in LOW_SIGNAL_LABELS for label in labels):
            low_signal_rows += 1
        if severity_column:
            severity_distribution.update([normalize_severity(row.get(severity_column, ""))])
        if safe_next_step_column:
            safe_next_step_distribution.update([categorize_safe_next_step(row.get(safe_next_step_column, ""))])
        if evidence_columns and not any(label in LOW_SIGNAL_LABELS or label in REJECT_LABELS for label in labels):
            if not has_any_value(row, evidence_columns):
                missing_evidence_span_count += 1

    usable_rows = max(0, reviewed_rows - rejected_rows - invalid_label_rows)
    invalid = bool(missing_required_columns or missing_required_values or invalid_label_rows)
    return {
        "status": "invalid" if invalid else "valid",
        "total_rows": len(rows),
        "reviewed_rows": reviewed_rows,
        "usable_rows": usable_rows,
        "rejected_rows": rejected_rows,
        "low_signal_rows": low_signal_rows,
        "missing_required_columns": missing_required_columns,
        "missing_required_values": missing_required_values,
        "invalid_label_rows": invalid_label_rows,
        "unknown_column_count": unknown_column_count,
        "missing_evidence_span_count": missing_evidence_span_count,
        "severity_distribution": safe_counter(severity_distribution),
        "cue_distribution": safe_counter(cue_distribution),
        "safe_next_step_distribution": safe_counter(safe_next_step_distribution),
    }


def main(argv: list[str] | None = None, *, restricted_root: Path = RESTRICTED_ROOT) -> int:
    parser = argparse.ArgumentParser(description="Validate local-only private gold-review labels without exposing row content.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=("csv", "xlsx"))
    args = parser.parse_args(argv)

    try:
        summary = validate_file(Path(args.input), file_format=args.format, restricted_root=restricted_root)
    except PrivateGoldLabelError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

