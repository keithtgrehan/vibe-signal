#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LABELS = REPO_ROOT / "data" / "review" / "human_label_template.jsonl"
DEFAULT_REPORT = REPO_ROOT / "reports" / "engine_eval" / "human_label_validation_report.md"
BLOCKED_CUE_IDS = {
    "hidden_intent",
    "cheating",
    "attraction",
    "diagnosis",
    "deception_certainty",
    "attachment_style",
    "neurotype",
    "true_emotion",
}
BLOCKED_TEXT_RE = re.compile(
    r"hidden intent|cheating|attraction|diagnos|deception certainty|attachment style|neurotype|true emotion|they like you|lying",
    re.IGNORECASE,
)
ALLOWED_CONFIDENCE = {"", "high", "medium", "low"}


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    candidate = str(value).strip().lower()
    if candidate in {"true", "1", "yes"}:
        return True
    if candidate in {"false", "0", "no"}:
        return False
    if candidate == "":
        return None
    return None


def validate_rows(rows: list[dict[str, Any]], *, require_human: bool = True) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    human_rows = 0
    for index, row in enumerate(rows, start=1):
        cue_id = str(row.get("cue_id", "")).strip()
        reviewer = str(row.get("reviewer", "")).strip()
        confidence = str(row.get("reviewer_confidence", "")).strip().lower()
        cue_present = _boolish(row.get("cue_present"))
        evidence_supports = _boolish(row.get("evidence_supports_cue"))
        unsafe_flag = _boolish(row.get("unsafe_wording_flag"))
        notes = " ".join(str(row.get(key, "")) for key in ("notes", "false_positive_reason", "false_negative_reason"))
        is_human_label = bool(reviewer and reviewer != "synthetic_bootstrap" and row.get("not_human_validated") is not True)
        if cue_id in BLOCKED_CUE_IDS:
            errors.append({"row": index, "field": "cue_id", "reason": "blocked_inference_category"})
        if is_human_label and BLOCKED_TEXT_RE.search(notes):
            errors.append({"row": index, "field": "notes", "reason": "unsafe_inference_language"})
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append({"row": index, "field": "reviewer_confidence", "reason": "invalid_confidence"})
        if cue_present is True and evidence_supports is not True:
            errors.append({"row": index, "field": "evidence_supports_cue", "reason": "present_cue_requires_supporting_evidence"})
        if unsafe_flag is True:
            errors.append({"row": index, "field": "unsafe_wording_flag", "reason": "unsafe_wording_requires_adjudication"})
        if is_human_label:
            human_rows += 1
    if require_human and human_rows == 0:
        errors.append({"row": 0, "field": "reviewer", "reason": "No human-reviewed labels available."})
    return {
        "status": "pass" if not errors else "fail",
        "row_count": len(rows),
        "human_reviewed_rows": human_rows,
        "errors": errors,
    }


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Human Label Validation Report",
        "",
        f"- Status: `{summary['status'].upper()}`",
        f"- Rows checked: `{summary['row_count']}`",
        f"- Human-reviewed rows: `{summary['human_reviewed_rows']}`",
        "",
        "Reviewers label observable wording only. This validator rejects hidden-intent, cheating, attraction, diagnosis, deception-certainty, attachment-style, neurotype, and true-emotion label categories.",
        "",
    ]
    if summary["errors"]:
        lines.extend(["## Errors", ""])
        lines.extend(f"- Row `{error['row']}` `{error['field']}`: {error['reason']}" for error in summary["errors"][:100])
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate human cue-label files with fail-closed safety rules.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    parser.add_argument("--allow-empty-human-review", action="store_true")
    args = parser.parse_args(argv)

    rows = _read_rows(Path(args.labels))
    summary = validate_rows(rows, require_human=not args.allow_empty_human_review)
    Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_out).write_text(build_report(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
