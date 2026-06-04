#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "data" / "review" / "human_review_packet_v2.jsonl"
DEFAULT_CSV = REPO_ROOT / "data" / "review" / "human_label_template.csv"
DEFAULT_JSONL = REPO_ROOT / "data" / "review" / "human_label_template.jsonl"


FIELDNAMES = [
    "review_id",
    "conversation_id",
    "split",
    "scenario",
    "message_id",
    "span_id",
    "cue_id",
    "cue_present",
    "evidence_text",
    "evidence_start",
    "evidence_end",
    "evidence_supports_cue",
    "false_positive_reason",
    "false_negative_reason",
    "unsafe_wording_flag",
    "low_signal_flag",
    "reviewer_confidence",
    "reviewer",
    "reviewed_at",
    "notes",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_template_rows(packet_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for packet in packet_rows:
        base = {
            "review_id": str(packet.get("review_id", "")),
            "conversation_id": str(packet.get("conversation_id", packet.get("fixture_id", ""))),
            "split": str(packet.get("split", "")),
            "scenario": str(packet.get("scenario", "")),
        }
        for cue in packet.get("candidate_cues", []):
            rows.append(
                {
                    **base,
                    "message_id": "",
                    "span_id": "",
                    "cue_id": str(cue),
                    "cue_present": "",
                    "evidence_text": "",
                    "evidence_start": "",
                    "evidence_end": "",
                    "evidence_supports_cue": "",
                    "false_positive_reason": "",
                    "false_negative_reason": "",
                    "unsafe_wording_flag": "false",
                    "low_signal_flag": "",
                    "reviewer_confidence": "",
                    "reviewer": "",
                    "reviewed_at": "",
                    "notes": "Observable wording only. Do not label hidden intent, cheating, attraction, diagnosis, true emotion, attachment style, or neurotype.",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare blank human label templates from the synthetic review packet.")
    parser.add_argument("--packet", default=str(DEFAULT_PACKET))
    parser.add_argument("--csv-out", default=str(DEFAULT_CSV))
    parser.add_argument("--jsonl-out", default=str(DEFAULT_JSONL))
    args = parser.parse_args(argv)

    packet_rows = read_jsonl(Path(args.packet))
    rows = build_template_rows(packet_rows)
    write_csv(Path(args.csv_out), rows)
    write_jsonl(Path(args.jsonl_out), rows)
    print(json.dumps({"status": "template_created", "packet_rows": len(packet_rows), "label_rows": len(rows)}, indent=2, sort_keys=True))
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
