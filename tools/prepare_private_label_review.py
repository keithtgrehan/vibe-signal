#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_ROOT = REPO_ROOT / "data" / "restricted" / "private_whatsapp"
DEFAULT_INPUT = RESTRICTED_ROOT / "processed" / "private_messages_redacted.jsonl"
DEFAULT_OUTPUT = RESTRICTED_ROOT / "processed" / "private_label_review.csv"

FIELDNAMES = [
    "example_id",
    "split",
    "speaker_roles",
    "text_window_redacted",
    "candidate_labels",
    "evidence_hint",
    "review_label",
    "severity",
    "safe_next_step",
    "reviewer_notes",
]

AMBIGUITY_RE = re.compile(r"\b(?:maybe|not sure|unclear|possibly|kind of|sort of|if you want|up to you)\b", re.IGNORECASE)
UNCLEAR_TIMING_RE = re.compile(r"\b(?:soon|later|sometime|at some point|eventually|tonight maybe|when you can)\b", re.IGNORECASE)
DIRECT_ASK_RE = re.compile(r"(?:\?|(?:^|\b)(?:can|could|would|will|please|do you|are you|can you|could you)\b)", re.IGNORECASE)
ANSWER_RE = re.compile(r"\b(?:yes|yeah|yep|no|nope|ok|okay|sure|confirmed|works|will do|cannot|can't|can not)\b", re.IGNORECASE)
TOPIC_SHIFT_RE = re.compile(r"\b(?:anyway|by the way|btw|different topic|also)\b", re.IGNORECASE)
PRESSURE_URGENCY_RE = re.compile(r"\b(?:right now|asap|urgent|immediately|you have to|must|need you to|why won't you|today)\b|!{2,}", re.IGNORECASE)
BOUNDARY_RE = re.compile(r"\b(?:no|stop|do not|don't|cannot|can't|not comfortable|need space|not available|i said no)\b", re.IGNORECASE)
REASSURANCE_RE = re.compile(r"\b(?:no pressure|no rush|no worries|all good|when you can|if you can|don't worry|take your time)\b", re.IGNORECASE)
REPAIR_RE = re.compile(r"\b(?:sorry|apologize|apology|let me rephrase|let me clarify|reset|start over|repair)\b", re.IGNORECASE)
ESCALATION_RE = re.compile(r"\b(?:frustrated|angry|always|never|this keeps happening|blame|ridiculous)\b|!{2,}", re.IGNORECASE)


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


def _text(row: dict[str, Any]) -> str:
    return str(row.get("text_redacted", row.get("text", "")))


def _has_direct_ask(text: str) -> bool:
    return bool(DIRECT_ASK_RE.search(text))


def candidate_labels_for_window(window: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    labels: list[str] = []
    hints: list[str] = []
    joined = "\n".join(_text(row) for row in window)
    checks = [
        ("ambiguity", AMBIGUITY_RE, "ambiguous wording marker"),
        ("unclear_timing", UNCLEAR_TIMING_RE, "unclear timing marker"),
        ("direct_ask", DIRECT_ASK_RE, "question or direct request marker"),
        ("pressure_urgency", PRESSURE_URGENCY_RE, "urgency or pressure wording marker"),
        ("boundary", BOUNDARY_RE, "boundary or refusal wording marker"),
        ("reassurance", REASSURANCE_RE, "reassurance wording marker"),
        ("repair_attempt", REPAIR_RE, "repair wording marker"),
        ("escalation_risk", ESCALATION_RE, "conflict intensity marker"),
    ]
    for label, pattern, hint in checks:
        if pattern.search(joined):
            labels.append(label)
            hints.append(hint)
    if len(window) >= 2:
        prior = window[-2]
        current = window[-1]
        prior_role = str(prior.get("speaker_role", ""))
        current_role = str(current.get("speaker_role", ""))
        current_text = _text(current)
        if (
            prior_role != current_role
            and _has_direct_ask(_text(prior))
            and not ANSWER_RE.search(current_text)
            and (TOPIC_SHIFT_RE.search(current_text) or not _has_direct_ask(current_text))
        ):
            labels.append("unanswered_ask_candidate")
            hints.append("prior direct ask lacks clear answer marker")
    return sorted(set(labels)), sorted(set(hints))


def build_windows(rows: list[dict[str, Any]], *, split: str = "private_review") -> list[dict[str, str]]:
    review_rows: list[dict[str, str]] = []
    for index in range(len(rows)):
        window = rows[max(0, index - 2) : index + 1]
        labels, hints = candidate_labels_for_window(window)
        text_window = "\n".join(f"{row.get('speaker_role', 'other')}: {_text(row)}" for row in window)
        review_rows.append(
            {
                "example_id": f"private_window_{index + 1:06d}",
                "split": split,
                "speaker_roles": "|".join(str(row.get("speaker_role", "other")) for row in window),
                "text_window_redacted": text_window,
                "candidate_labels": ";".join(labels),
                "evidence_hint": ";".join(hints),
                "review_label": "",
                "severity": "",
                "safe_next_step": "",
                "reviewer_notes": "",
            }
        )
    return review_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    safe_path = ensure_restricted_path(path, kind="review CSV")
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    with safe_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare restricted redacted WhatsApp windows for local cue-label review.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--split", default="private_review")
    args = parser.parse_args(argv)

    try:
        rows = read_jsonl(Path(args.input))
        review_rows = build_windows(rows, split=args.split)
        write_csv(Path(args.output), review_rows)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    label_count = sum(1 for row in review_rows if row["candidate_labels"])
    printable = {
        "status": "complete",
        "windows_written": len(review_rows),
        "windows_with_candidate_labels": label_count,
    }
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0 if review_rows else 1


if __name__ == "__main__":
    raise SystemExit(main())

