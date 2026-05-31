from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .objects import validate_evidence_object


def write_evidence_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    errors: list[str] = []
    for index, row in enumerate(materialized, start=1):
        for error in validate_evidence_object(row):
            errors.append(f"row {index}: {error}")
    if errors:
        raise ValueError("; ".join(errors))
    with output_path.open("w", encoding="utf-8") as handle:
        for row in materialized:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_evidence_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"line {line_number}: expected JSON object")
            rows.append(row)
    return rows
