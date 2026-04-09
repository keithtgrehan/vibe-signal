"""Generic pasted-chat parser."""

from __future__ import annotations

from datetime import datetime
import re
from pathlib import Path
from typing import Any

from .normalization import enrich_messages

_STAMPED_RE = re.compile(
    r"^\[?(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?)\]?\s+(?P<speaker>[^:]+):\s?(?P<text>.*)$"
)
_SPEAKER_RE = re.compile(r"^(?P<speaker>[^:]{1,40}):\s?(?P<text>.*)$")


def _parse_timestamp(raw: str | None) -> str | None:
    if not raw:
        return None
    candidate = raw.replace("T", " ").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(candidate, fmt).isoformat()
        except ValueError:
            continue
    return None


def parse_chat_text(text: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in str(text or "").splitlines():
        line = raw_line.rstrip()
        if not line:
            continue

        stamped = _STAMPED_RE.match(line)
        simple = _SPEAKER_RE.match(line) if stamped is None else None

        if stamped or simple:
            if current is not None:
                messages.append(current)

            match = stamped or simple
            speaker = match.group("speaker").strip()
            body = match.group("text").strip()
            timestamp = _parse_timestamp(stamped.group("timestamp")) if stamped else None
            current = {
                "message_id": len(messages) + 1,
                "speaker": speaker,
                "timestamp": timestamp,
                "text": body,
                "is_system": False,
                "source": "pasted_chat",
            }
            continue

        if current is not None:
            current["text"] = f"{current['text']}\n{line}".strip()

    if current is not None:
        messages.append(current)

    return enrich_messages(messages)


def parse_chat_file(path: str | Path) -> list[dict[str, Any]]:
    return parse_chat_text(Path(path).read_text(encoding="utf-8"))
