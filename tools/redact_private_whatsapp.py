#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_ROOT = REPO_ROOT / "data" / "restricted" / "private_whatsapp"
DEFAULT_INPUT = RESTRICTED_ROOT / "processed" / "private_messages.jsonl"
DEFAULT_OUTPUT = RESTRICTED_ROOT / "processed" / "private_messages_redacted.jsonl"
DEFAULT_STATS = RESTRICTED_ROOT / "processed" / "private_redaction_stats.json"

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
URL_RE = re.compile(r"\b(?:https?://|www\.)\S+\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{6,}\d)(?!\w)")
DATE_RE = re.compile(r"\b(?:\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?|\d{4}-\d{2}-\d{2})\b")
TIME_RE = re.compile(r"\b(?:\d{1,2}:\d{2}(?::\d{2})?|\d{1,2}\s?(?:am|pm))\b", re.IGNORECASE)
NAME_RE = re.compile(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?\b")
NAME_EXCLUSIONS = {
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
}


def ensure_restricted_path(path: Path, *, kind: str = "path") -> Path:
    resolved = path.resolve()
    restricted = RESTRICTED_ROOT.resolve()
    if resolved != restricted and restricted not in resolved.parents:
        raise ValueError(f"{kind} must be under {RESTRICTED_ROOT.relative_to(REPO_ROOT)}")
    return resolved


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    safe_path = ensure_restricted_path(path, kind="input JSONL")
    if not safe_path.exists():
        raise FileNotFoundError(f"input JSONL not found: {path}")
    return [json.loads(line) for line in safe_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _replace(pattern: re.Pattern[str], text: str, replacement: str, counts: Counter[str], key: str) -> str:
    text, count = pattern.subn(replacement, text)
    counts[key] += count
    return text


def _replace_names(text: str, counts: Counter[str]) -> str:
    def repl(match: re.Match[str]) -> str:
        value = match.group(0)
        if value in NAME_EXCLUSIONS:
            return value
        counts["names"] += 1
        return "[NAME]"

    return NAME_RE.sub(repl, text)


def redact_text(text: str, *, redact_dates_times: bool = True) -> tuple[str, Counter[str]]:
    counts: Counter[str] = Counter()
    redacted = _replace(EMAIL_RE, text, "[EMAIL]", counts, "emails")
    redacted = _replace(URL_RE, redacted, "[URL]", counts, "urls")
    redacted = _replace(PHONE_RE, redacted, "[PHONE]", counts, "phones")
    if redact_dates_times:
        redacted = _replace(DATE_RE, redacted, "[DATE]", counts, "dates")
        redacted = _replace(TIME_RE, redacted, "[TIME]", counts, "times")
    redacted = _replace_names(redacted, counts)
    return redacted, counts


def redact_rows(rows: list[dict[str, Any]], *, redact_dates_times: bool = True) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output_rows: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    for index, row in enumerate(rows, start=1):
        redacted_text, counts = redact_text(str(row.get("text", "")), redact_dates_times=redact_dates_times)
        totals.update(counts)
        output_rows.append(
            {
                "message_id": str(row.get("message_id", f"private_whatsapp_{index:06d}")),
                "turn_index": row.get("turn_index", index),
                "speaker_role": str(row.get("speaker_role", "other")),
                "text_redacted": redacted_text,
            }
        )
    stats = {
        "status": "complete",
        "rows_read": len(rows),
        "rows_written": len(output_rows),
        "replacement_counts": dict(sorted(totals.items())),
    }
    return output_rows, stats


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    safe_path = ensure_restricted_path(path, kind="output JSONL")
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    with safe_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n")


def write_stats(path: Path, stats: dict[str, Any]) -> None:
    safe_path = ensure_restricted_path(path, kind="stats output")
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Redact restricted WhatsApp JSONL for local cue-label review.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--stats-out", default=str(DEFAULT_STATS))
    parser.add_argument("--keep-dates-times", action="store_true", help="Keep date and time strings in the redacted text.")
    args = parser.parse_args(argv)

    try:
        rows = read_jsonl(Path(args.input))
        output_rows, stats = redact_rows(rows, redact_dates_times=not args.keep_dates_times)
        write_jsonl(Path(args.output), output_rows)
        write_stats(Path(args.stats_out), stats)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    printable = {
        "status": stats["status"],
        "rows_read": stats["rows_read"],
        "rows_written": stats["rows_written"],
        "replacement_counts": stats["replacement_counts"],
    }
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
