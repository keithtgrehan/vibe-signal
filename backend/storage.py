from __future__ import annotations

import hashlib
import re
from time import time
from typing import Any


FEEDBACK_ROWS: list[dict[str, Any]] = []
EVENT_ROWS: list[dict[str, Any]] = []
SAFE_EVENT_ID_RE = re.compile(
    r"^(?:evt|event)[A-Za-z0-9_.:-]{0,76}$"
    r"|^[0-9a-fA-F]{32}$"
    r"|^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
SAFE_TIMESTAMP_RE = re.compile(r"^[0-9]{10,17}(?:\.[0-9]{1,6})?$")


def _hash_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _safe_event_id(value: Any, fallback: str) -> str:
    candidate = str(value or "").strip()
    if candidate and SAFE_EVENT_ID_RE.fullmatch(candidate):
        return candidate[:80]
    return fallback


def _safe_client_timestamp(value: Any) -> str:
    candidate = str(value or "").strip()
    if SAFE_TIMESTAMP_RE.fullmatch(candidate):
        return candidate[:24]
    return ""


def store_feedback_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    comment = str(payload.get("comment", ""))
    feedback_event_id = _safe_event_id(payload.get("feedback_event_id"), "")
    if feedback_event_id:
        for existing in FEEDBACK_ROWS:
            if existing.get("feedback_event_id") == feedback_event_id:
                return {**existing, "duplicate": True}

    row = {
        "feedback_id": f"feedback_{len(FEEDBACK_ROWS) + 1:06d}",
        "feedback_event_id": feedback_event_id,
        "match_id": str(payload.get("match_id", "")),
        "rating": payload.get("rating"),
        "comment_length": len(comment),
        "comment_sha256": _hash_text(comment) if comment else "",
        "stored_at_unix": round(time(), 3),
    }
    FEEDBACK_ROWS.append(row)
    return row


def store_event_metadata(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    fallback_event_id = f"{event_type}_{len(EVENT_ROWS) + 1:06d}"
    event_id = _safe_event_id(payload.get("event_id"), fallback_event_id)
    if event_id != fallback_event_id:
        for existing in EVENT_ROWS:
            if existing.get("event_id") == event_id and existing.get("event_type") == event_type:
                return {**existing, "duplicate": True}

    row = {
        "event_id": event_id,
        "event_type": event_type,
        "client_timestamp": _safe_client_timestamp(payload.get("client_timestamp")),
        "stored_at_unix": round(time(), 3),
        "payload_field_count": len(payload),
    }
    EVENT_ROWS.append(row)
    return row
