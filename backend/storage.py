from __future__ import annotations

import hashlib
from time import time
from typing import Any


FEEDBACK_ROWS: list[dict[str, Any]] = []
EVENT_ROWS: list[dict[str, Any]] = []


def _hash_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def store_feedback_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    comment = str(payload.get("comment", ""))
    row = {
        "feedback_id": f"feedback_{len(FEEDBACK_ROWS) + 1:06d}",
        "match_id": str(payload.get("match_id", "")),
        "rating": payload.get("rating"),
        "comment_length": len(comment),
        "comment_sha256": _hash_text(comment) if comment else "",
        "stored_at_unix": round(time(), 3),
    }
    FEEDBACK_ROWS.append(row)
    return row


def store_event_metadata(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    row = {
        "event_id": str(payload.get("event_id", f"{event_type}_{len(EVENT_ROWS) + 1:06d}")),
        "event_type": event_type,
        "client_timestamp": str(payload.get("client_timestamp", "")),
        "stored_at_unix": round(time(), 3),
        "payload_field_count": len(payload),
    }
    EVENT_ROWS.append(row)
    return row
