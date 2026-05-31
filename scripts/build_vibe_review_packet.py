#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vibesignal_ai.evidence.export import load_evidence_jsonl  # noqa: E402
from vibesignal_ai.evidence.objects import validate_evidence_object  # noqa: E402


CSV_COLUMNS = [
    "conversation_id",
    "evidence_id",
    "cue_name",
    "speaker_role",
    "evidence_text",
    "interpretation_limits",
    "reviewer_label_type",
    "reviewer_confidence",
    "reviewer_notes",
    "accept/reject",
]


INTRO = """# Vibe Review Packet

Machine cues are suggestions. The reviewer decides which labels, if any, are accepted.

Accepted labels need evidence spans. Use this packet for communication-pattern review only: no emotion/deception/intent/diagnosis claims, no attraction or attachment-style claims, and no protected-trait or neurodivergence inference.
"""


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        for error in validate_evidence_object(row):
            errors.append(f"row {index}: {error}")
    return errors


def build_packet_rows(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    packet_rows: list[dict[str, str]] = []
    for row in rows:
        packet_rows.append(
            {
                "conversation_id": str(row.get("conversation_id", "")),
                "evidence_id": str(row.get("evidence_id", "")),
                "cue_name": str(row.get("cue_name", "")),
                "speaker_role": str(row.get("speaker_role", "")),
                "evidence_text": str(row.get("evidence_text", "")),
                "interpretation_limits": json.dumps(row.get("interpretation_limits", {}), sort_keys=True),
                "reviewer_label_type": "",
                "reviewer_confidence": "",
                "reviewer_notes": "",
                "accept/reject": "",
            }
        )
    return packet_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(rows: list[dict[str, str]]) -> str:
    lines = [INTRO.rstrip(), ""]
    for row in rows:
        lines.extend(
            [
                f"## {row['evidence_id'] or 'unidentified_evidence'}",
                "",
                f"- conversation_id: {row['conversation_id']}",
                f"- cue_name: {row['cue_name']}",
                f"- speaker_role: {row['speaker_role']}",
                f"- evidence_text: {row['evidence_text']}",
                f"- interpretation_limits: `{row['interpretation_limits']}`",
                "- reviewer_label_type: ",
                "- reviewer_confidence: ",
                "- reviewer_notes: ",
                "- accept/reject: ",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Vibe review packet from evidence objects.")
    parser.add_argument("--evidence", required=True, help="Input evidence_objects.jsonl path.")
    parser.add_argument("--md-out", default="data/review/vibe_review_packet.md")
    parser.add_argument("--csv-out", default="data/review/vibe_review_packet.csv")
    parser.add_argument("--allow-invalid", action="store_true", help="Build packet even if evidence validation fails.")
    args = parser.parse_args(argv)

    try:
        evidence_rows = load_evidence_jsonl(args.evidence)
        errors = validate_rows(evidence_rows)
    except Exception as exc:
        errors = [str(exc)]
        evidence_rows = []

    if errors and not args.allow_invalid:
        print("Invalid evidence; refusing to build review packet:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    packet_rows = build_packet_rows(evidence_rows)
    write_csv(Path(args.csv_out), packet_rows)
    md_path = Path(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(packet_rows), encoding="utf-8")
    print(json.dumps({"status": "ok", "rows": len(packet_rows), "md_out": args.md_out, "csv_out": args.csv_out}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
