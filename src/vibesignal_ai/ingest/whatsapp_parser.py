"""WhatsApp export parsing utilities."""

from __future__ import annotations

from datetime import datetime
import re
from pathlib import Path
from typing import Any

from .normalization import enrich_messages

_MESSAGE_RE = re.compile(r"^(?P<timestamp>.+?)\s-\s(?P<body>.+)$")
_TIMESTAMP_FORMATS = (
    "%m/%d/%y, %I:%M %p",
    "%m/%d/%Y, %I:%M %p",
    "%d/%m/%y, %H:%M",
    "%d/%m/%Y, %H:%M",
    "%d.%m.%y, %H:%M",
    "%d.%m.%Y, %H:%M",
    "%Y-%m-%d, %H:%M",
    "%Y-%m-%d %H:%M",
)


def _clean_timestamp(value: str) -> str:
    return (
        value.replace("\u202f", " ")
        .replace("\u00a0", " ")
        .replace("[", "")
        .replace("]", "")
        .strip()
    )


def parse_timestamp(raw: str) -> str | None:
    candidate = _clean_timestamp(raw)
    for fmt in _TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(candidate, fmt).isoformat()
        except ValueError:
            continue
    return None


def _line_starts_message(line: str) -> bool:
    return bool(_MESSAGE_RE.match(line.strip()))


def _split_body(body: str) -> tuple[str, str, bool]:
    if ":" not in body:
        return "system", body.strip(), True
    speaker, text = body.split(":", 1)
    speaker = speaker.strip().lstrip("~")
    if not speaker:
        return "system", body.strip(), True
    return speaker, text.strip(), False


def parse_whatsapp_text(text: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in str(text or "").splitlines():
        line = raw_line.rstrip("\n")
        if not line.strip():
            if current is not None:
                current["text"] = current["text"].rstrip()
            continue

        if _line_starts_message(line):
            match = _MESSAGE_RE.match(line.strip())
            if match is None:
                continue
            if current is not None:
                messages.append(current)

            timestamp = parse_timestamp(match.group("timestamp"))
            speaker, body_text, is_system = _split_body(match.group("body"))
            current = {
                "message_id": len(messages) + 1,
                "speaker": speaker,
                "timestamp": timestamp,
                "text": body_text,
                "is_system": is_system,
                "source": "whatsapp_export",
            }
            continue

        if current is None:
            continue
        current["text"] = f"{current['text']}\n{line}".strip()

    if current is not None:
        messages.append(current)

    return enrich_messages(messages)


def parse_whatsapp_file(path: str | Path) -> list[dict[str, Any]]:
    return parse_whatsapp_text(Path(path).read_text(encoding="utf-8"))
