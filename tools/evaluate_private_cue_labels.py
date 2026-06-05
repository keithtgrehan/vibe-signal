#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_ROOT = REPO_ROOT / "data" / "restricted" / "private_whatsapp"
DEFAULT_INPUT = RESTRICTED_ROOT / "processed" / "private_label_review.csv"
DEFAULT_REPORT = RESTRICTED_ROOT / "processed" / "private_label_evaluation.md"


def ensure_restricted_path(path: Path, *, kind: str = "path") -> Path:
    resolved = path.resolve()
    restricted = RESTRICTED_ROOT.resolve()
    if resolved != restricted and restricted not in resolved.parents:
        raise ValueError(f"{kind} must be under {RESTRICTED_ROOT.relative_to(REPO_ROOT)}")
    return resolved


def split_labels(value: str) -> list[str]:
    normalized = value.replace("|", ";").replace(",", ";")
    return [item.strip() for item in normalized.split(";") if item.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    safe_path = ensure_restricted_path(path, kind="review CSV")
    if not safe_path.exists():
        raise FileNotFoundError(f"review CSV not found: {path}")
    with safe_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def compute_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    candidate_counts: Counter[str] = Counter()
    review_counts: Counter[str] = Counter()
    reviewed_rows = 0
    candidate_hit = 0
    candidate_miss = 0
    for row in rows:
        candidates = set(split_labels(row.get("candidate_labels", "")))
        candidate_counts.update(candidates)
        reviewed = split_labels(row.get("review_label", ""))
        if not reviewed:
            continue
        reviewed_rows += 1
        review_counts.update(reviewed)
        if any(label in candidates for label in reviewed):
            candidate_hit += 1
        else:
            candidate_miss += 1
    agreement = round(candidate_hit / reviewed_rows, 4) if reviewed_rows else None
    return {
        "status": "complete",
        "row_count": len(rows),
        "reviewed_rows": reviewed_rows,
        "candidate_hit": candidate_hit,
        "candidate_miss": candidate_miss,
        "candidate_review_agreement": agreement,
        "candidate_counts": dict(sorted(candidate_counts.items())),
        "review_counts": dict(sorted(review_counts.items())),
    }


def build_report(summary: dict[str, Any]) -> str:
    candidate_lines = [f"- `{label}`: `{count}`" for label, count in summary["candidate_counts"].items()] or ["- None"]
    review_lines = [f"- `{label}`: `{count}`" for label, count in summary["review_counts"].items()] or ["- None"]
    agreement = summary["candidate_review_agreement"]
    agreement_text = "`not available`" if agreement is None else f"`{agreement}`"
    return "\n".join(
        [
            "# Private Cue Label Review Evaluation",
            "",
            "Aggregate local report only. It contains no raw or redacted message text.",
            "",
            f"- Rows: `{summary['row_count']}`",
            f"- Reviewed rows: `{summary['reviewed_rows']}`",
            f"- Candidate hit rows: `{summary['candidate_hit']}`",
            f"- Candidate miss rows: `{summary['candidate_miss']}`",
            f"- Candidate/review agreement: {agreement_text}",
            "",
            "## Candidate Counts",
            "",
            *candidate_lines,
            "",
            "## Review Counts",
            "",
            *review_lines,
            "",
            "These counts are not model-quality proof, real-world accuracy, or production readiness.",
            "",
        ]
    )


def write_report(path: Path, report: str) -> None:
    safe_path = ensure_restricted_path(path, kind="report output")
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_text(report, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate restricted private cue labels in aggregate.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    args = parser.parse_args(argv)

    try:
        rows = read_csv(Path(args.input))
        summary = compute_summary(rows)
        write_report(Path(args.report_out), build_report(summary))
    except (FileNotFoundError, ValueError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    printable = {
        "status": summary["status"],
        "row_count": summary["row_count"],
        "reviewed_rows": summary["reviewed_rows"],
        "candidate_hit": summary["candidate_hit"],
        "candidate_miss": summary["candidate_miss"],
        "candidate_review_agreement": summary["candidate_review_agreement"],
    }
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
