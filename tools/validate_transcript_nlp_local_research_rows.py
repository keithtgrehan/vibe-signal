#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.transcript_nlp_local_research_common import (  # noqa: E402
    LOCAL_SOURCE_TIERS,
    aggregate_row_counts,
    read_jsonl,
    validate_local_research_row,
    write_json,
)
from tools.validate_synthetic_whatsapp_training_rows import validate_row as validate_synthetic_row  # noqa: E402


SOURCE_ALIASES = {
    "goemotions": "goemotions_local_research_apache2",
    "meld": "meld_local_research_gpl3_nc",
}


def _parse_augmentation_arg(value: str) -> tuple[str, Path]:
    if ":" not in value:
        raise ValueError("--augmentation-input must use source:path")
    source, path_text = value.split(":", 1)
    source = source.strip().lower()
    if source not in SOURCE_ALIASES:
        raise ValueError(f"unsupported augmentation source {source!r}")
    return SOURCE_ALIASES[source], Path(path_text)


def validate_inputs(synthetic_input: Path, augmentation_inputs: list[str]) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    all_rows: list[dict[str, Any]] = []
    synthetic_rows = read_jsonl(synthetic_input)
    for index, row in enumerate(synthetic_rows, start=1):
        row_errors = validate_synthetic_row(row, index)
        errors.extend(f"synthetic {error}" for error in row_errors)
    all_rows.extend(synthetic_rows)

    augmentation_counts: Counter[str] = Counter()
    for raw in augmentation_inputs:
        expected_source_tier, path = _parse_augmentation_arg(raw)
        rows = read_jsonl(path)
        for index, row in enumerate(rows, start=1):
            if row.get("source_tier") != expected_source_tier:
                errors.append(f"{path}: row {index}: source_tier must be {expected_source_tier}")
            if row.get("source_tier") not in LOCAL_SOURCE_TIERS:
                errors.append(f"{path}: row {index}: unsupported local source_tier")
            row_errors = validate_local_research_row(row, index)
            errors.extend(f"{path}: {error}" for error in row_errors)
            augmentation_counts[str(row.get("source_tier", "unknown"))] += 1
        all_rows.extend(rows)

    summary = aggregate_row_counts(all_rows)
    summary.update(
        {
            "status": "valid" if not errors else "invalid",
            "synthetic_row_count": len(synthetic_rows),
            "augmentation_row_counts": dict(sorted(augmentation_counts.items())),
            "errors": errors,
        }
    )
    return errors, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate synthetic plus local external transcript NLP research rows.")
    parser.add_argument("--synthetic-input", required=True)
    parser.add_argument("--augmentation-input", action="append", default=[])
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    try:
        errors, summary = validate_inputs(Path(args.synthetic_input), args.augmentation_input)
    except Exception as exc:
        errors = [str(exc)]
        summary = {"status": "invalid", "row_count": 0, "errors": errors}

    if args.json_out:
        write_json(Path(args.json_out), summary)

    if errors:
        print(f"Transcript NLP local research row validation failed: {len(errors)} error(s).", file=sys.stderr)
        for error in errors[:100]:
            print(f"- {error}", file=sys.stderr)
        if len(errors) > 100:
            print(f"- ... {len(errors) - 100} more error(s)", file=sys.stderr)
        return 1

    print(
        f"Transcript NLP local research row validation passed: "
        f"{summary['row_count']} total row(s), {summary['synthetic_row_count']} synthetic row(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
