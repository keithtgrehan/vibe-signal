#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_ROOT = REPO_ROOT / "data" / "restricted" / "private_whatsapp"
DEFAULT_INPUT = RESTRICTED_ROOT / "processed" / "private_messages_redacted.jsonl"
DEFAULT_OUTPUT = RESTRICTED_ROOT / "processed" / "private_label_review.csv"
DEFAULT_SEED = 42

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
LABEL_CONFIDENCE = {
    "ambiguity": 0.68,
    "unclear_timing": 0.7,
    "direct_ask": 0.74,
    "unanswered_ask_candidate": 0.64,
    "pressure_urgency": 0.72,
    "boundary": 0.7,
    "reassurance": 0.75,
    "repair_attempt": 0.74,
    "escalation_risk": 0.66,
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


def candidate_confidence(labels: list[str]) -> float:
    if not labels:
        return 0.0
    base = max(LABEL_CONFIDENCE.get(label, 0.6) for label in labels)
    return round(min(0.95, base + (0.03 if len(labels) >= 2 else 0.0)), 4)


def split_label_list(value: str) -> list[str]:
    return [item.strip() for item in value.replace("|", ",").replace(";", ",").split(",") if item.strip()]


def build_windows(
    rows: list[dict[str, Any]],
    *,
    split: str = "private_review",
    window_size: int = 3,
    min_confidence: float = 0.0,
) -> list[dict[str, str]]:
    bounded_window_size = max(1, min(3, int(window_size)))
    review_rows: list[dict[str, str]] = []
    for index in range(len(rows)):
        window = rows[max(0, index - bounded_window_size + 1) : index + 1]
        labels, hints = candidate_labels_for_window(window)
        if candidate_confidence(labels) < float(min_confidence):
            continue
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


def select_review_rows(
    rows: list[dict[str, str]],
    *,
    limit: int | None = None,
    seed: int = DEFAULT_SEED,
    prioritize_labels: list[str] | None = None,
) -> list[dict[str, str]]:
    if limit is None or limit <= 0 or len(rows) <= limit:
        return rows

    rng = random.Random(seed)
    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()
    by_label: dict[str, list[dict[str, str]]] = defaultdict(list)
    labeled_rows: list[dict[str, str]] = []
    unlabeled_rows: list[dict[str, str]] = []
    for row in rows:
        labels = split_label_list(row.get("candidate_labels", ""))
        if labels:
            labeled_rows.append(row)
        else:
            unlabeled_rows.append(row)
        for label in labels:
            by_label[label].append(row)

    label_order = list(prioritize_labels or sorted(by_label))
    for label in label_order:
        by_label[label].sort(key=lambda row: row["example_id"])
        rng.shuffle(by_label[label])

    while len(selected) < limit and any(by_label.get(label) for label in label_order):
        progressed = False
        for label in label_order:
            bucket = by_label.get(label, [])
            while bucket:
                row = bucket.pop(0)
                if row["example_id"] in selected_ids:
                    continue
                selected.append(row)
                selected_ids.add(row["example_id"])
                progressed = True
                break
            if len(selected) >= limit:
                break
        if not progressed:
            break

    remainder = [row for row in labeled_rows if row["example_id"] not in selected_ids]
    remainder.sort(key=lambda row: row["example_id"])
    rng.shuffle(remainder)
    for row in remainder:
        if len(selected) >= limit:
            break
        selected.append(row)
        selected_ids.add(row["example_id"])

    fallback = [row for row in unlabeled_rows if row["example_id"] not in selected_ids]
    fallback.sort(key=lambda row: row["example_id"])
    rng.shuffle(fallback)
    for row in fallback:
        if len(selected) >= limit:
            break
        selected.append(row)
        selected_ids.add(row["example_id"])

    return sorted(selected, key=lambda row: row["example_id"])


def build_stats(
    *,
    input_rows: int,
    all_windows: list[dict[str, str]],
    selected_rows: list[dict[str, str]],
    split: str,
    window_size: int,
    min_confidence: float,
    prioritize_labels: list[str],
    seed: int,
) -> dict[str, Any]:
    def label_counts(rows: list[dict[str, str]]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for row in rows:
            counter.update(split_label_list(row.get("candidate_labels", "")))
        return dict(sorted(counter.items()))

    hint_counter: Counter[str] = Counter()
    for row in selected_rows:
        hint_counter.update(split_label_list(row.get("evidence_hint", "")))
    return {
        "status": "complete",
        "input_rows": input_rows,
        "all_windows": len(all_windows),
        "rows_written": len(selected_rows),
        "windows_with_candidate_labels": sum(1 for row in selected_rows if row.get("candidate_labels")),
        "all_candidate_label_counts": label_counts(all_windows),
        "candidate_label_counts": label_counts(selected_rows),
        "evidence_hint_counts": dict(sorted(hint_counter.items())),
        "rows_needing_human_review": sum(1 for row in selected_rows if not row.get("review_label", "").strip()),
        "split": split,
        "window_size": max(1, min(3, int(window_size))),
        "min_confidence": float(min_confidence),
        "prioritize_labels": prioritize_labels,
        "seed": seed,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    safe_path = ensure_restricted_path(path, kind="review CSV")
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    with safe_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_stats(path: Path, stats: dict[str, Any]) -> None:
    safe_path = ensure_restricted_path(path, kind="stats output")
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare restricted redacted WhatsApp windows for local cue-label review.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--split", default="private_review")
    parser.add_argument("--limit", type=int, help="Optional deterministic row limit for a review packet.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--prioritize-labels", default="", help="Comma-separated labels to balance first when sampling.")
    parser.add_argument("--window-size", type=int, default=3, help="Number of recent turns per window, bounded to 1-3.")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Minimum weak-label confidence for selected windows.")
    parser.add_argument("--stats-out", help="Restricted aggregate JSON stats output.")
    args = parser.parse_args(argv)

    try:
        rows = read_jsonl(Path(args.input))
        priority_labels = split_label_list(args.prioritize_labels)
        review_rows = build_windows(rows, split=args.split, window_size=args.window_size, min_confidence=args.min_confidence)
        selected_rows = select_review_rows(review_rows, limit=args.limit, seed=args.seed, prioritize_labels=priority_labels)
        write_csv(Path(args.output), selected_rows)
        stats_path = Path(args.stats_out) if args.stats_out else Path(args.output).with_name(f"{Path(args.output).stem}_stats.json")
        stats = build_stats(
            input_rows=len(rows),
            all_windows=review_rows,
            selected_rows=selected_rows,
            split=args.split,
            window_size=args.window_size,
            min_confidence=args.min_confidence,
            prioritize_labels=priority_labels,
            seed=args.seed,
        )
        write_stats(stats_path, stats)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    printable = {
        "status": "complete",
        "windows_written": len(selected_rows),
        "windows_with_candidate_labels": stats["windows_with_candidate_labels"],
        "stats_path": str(ensure_restricted_path(stats_path, kind="stats output").relative_to(REPO_ROOT)),
    }
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0 if selected_rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
