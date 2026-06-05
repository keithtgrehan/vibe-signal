#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_ROOT = REPO_ROOT / "data" / "restricted" / "private_whatsapp"
DEFAULT_OUTPUT_DIR = RESTRICTED_ROOT / "processed"
CHAT_LINE_RE = re.compile(
    r"^\[(?P<date>\d{2}\.\d{2}\.\d{2}), (?P<time>\d{2}:\d{2}:\d{2})\] (?P<sender>[^:]+): (?P<message>.*)$"
)


@dataclass
class ParsedMessage:
    timestamp: str
    speaker_role: str
    text: str
    source_file: str
    multiline: bool = False


def ensure_restricted_path(path: Path, *, kind: str = "path") -> Path:
    resolved = path.resolve()
    restricted = RESTRICTED_ROOT.resolve()
    if resolved != restricted and restricted not in resolved.parents:
        raise ValueError(f"{kind} must be under {RESTRICTED_ROOT.relative_to(REPO_ROOT)}")
    return resolved


def speaker_role(sender: str) -> str:
    normalized = sender.strip().casefold()
    return "self" if normalized in {"keith", "self"} else "other"


def _decode_chat_bytes(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_chat_text(text: str, *, source_file: str = "_chat.txt") -> list[ParsedMessage]:
    messages: list[ParsedMessage] = []
    current: ParsedMessage | None = None
    for line in text.splitlines():
        match = CHAT_LINE_RE.match(line)
        if match:
            if current is not None:
                messages.append(current)
            current = ParsedMessage(
                timestamp=f"{match.group('date')} {match.group('time')}",
                speaker_role=speaker_role(match.group("sender")),
                text=match.group("message"),
                source_file=source_file,
            )
            continue
        if current is not None:
            current.text = f"{current.text}\n{line}" if current.text else line
            current.multiline = True
    if current is not None:
        messages.append(current)
    return messages


def read_chat_zip(zip_path: Path) -> tuple[list[ParsedMessage], dict[str, Any]]:
    if not zip_path.exists():
        raise FileNotFoundError(f"zip not found: {zip_path}")
    messages: list[ParsedMessage] = []
    chat_files = 0
    skipped_files = 0
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            name = Path(member.filename).name
            if member.is_dir() or not name.endswith("_chat.txt"):
                skipped_files += 1
                continue
            chat_files += 1
            chat_text = _decode_chat_bytes(archive.read(member))
            messages.extend(parse_chat_text(chat_text, source_file=f"chat_{chat_files:03d}"))
    stats = {
        "chat_files": chat_files,
        "skipped_files": skipped_files,
        "parsed_messages": len(messages),
        "multiline_messages": sum(1 for message in messages if message.multiline),
        "speaker_role_counts": dict(Counter(message.speaker_role for message in messages)),
    }
    return messages, stats


def write_outputs(messages: list[ParsedMessage], stats: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    safe_output_dir = ensure_restricted_path(output_dir, kind="output directory")
    safe_output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = safe_output_dir / "private_messages.jsonl"
    stats_path = safe_output_dir / "private_ingest_stats.json"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for index, message in enumerate(messages, start=1):
            row = {
                "message_id": f"private_whatsapp_{index:06d}",
                "turn_index": index,
                "timestamp": message.timestamp,
                "speaker_role": message.speaker_role,
                "text": message.text,
                "source_file_index": message.source_file,
            }
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n")
    summary = {
        **stats,
        "status": "complete",
        "jsonl_path": str(jsonl_path.relative_to(REPO_ROOT)),
        "stats_path": str(stats_path.relative_to(REPO_ROOT)),
    }
    stats_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest a local WhatsApp export into the restricted private review area.")
    parser.add_argument("--zip-path", required=True, help="Path to a local WhatsApp export zip.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Restricted output directory.")
    args = parser.parse_args(argv)

    try:
        output_dir = ensure_restricted_path(Path(args.output_dir), kind="output directory")
        messages, stats = read_chat_zip(Path(args.zip_path))
        summary = write_outputs(messages, stats, output_dir)
    except (FileNotFoundError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    printable = {
        "status": summary["status"],
        "chat_files": summary["chat_files"],
        "parsed_messages": summary["parsed_messages"],
        "multiline_messages": summary["multiline_messages"],
        "speaker_role_counts": summary["speaker_role_counts"],
        "jsonl_path": summary["jsonl_path"],
        "stats_path": summary["stats_path"],
    }
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
