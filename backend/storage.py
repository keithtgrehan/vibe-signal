from __future__ import annotations

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
SAFE_METADATA_TOKEN_RE = re.compile(r"[^A-Za-z0-9_.:-]+")
ALLOWED_MONITORING_EVENT_TYPES = {
    "analysis_started",
    "analysis_succeeded",
    "analysis_failed",
    "safety_blocked",
    "low_signal_fallback",
    "synthetic_demo_started",
    "synthetic_demo_completed",
    "user_feedback_useful",
    "user_feedback_too_strong",
    "user_feedback_missed_context",
    "user_feedback_unsafe_wording",
    "user_feedback_confusing",
}


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


def _safe_metadata_token(value: Any, max_length: int = 48) -> str:
    candidate = SAFE_METADATA_TOKEN_RE.sub("_", str(value or "").strip())
    return candidate[:max_length]


def _safe_monitoring_event_type(value: Any) -> str:
    candidate = str(value or "").strip()
    if candidate in ALLOWED_MONITORING_EVENT_TYPES:
        return candidate
    return "unspecified"


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
        "feedback_tag": _safe_metadata_token(payload.get("feedback_tag"), 32),
        "cue_id": _safe_metadata_token(payload.get("cue_id"), 48),
        "cue_family": _safe_metadata_token(payload.get("cue_family"), 48),
        "evidence_quality": _safe_metadata_token(payload.get("evidence_quality"), 24),
        "goal_id": _safe_metadata_token(payload.get("goal_id"), 32),
        "context_id": _safe_metadata_token(payload.get("context_id"), 32),
        "analysis_style_id": _safe_metadata_token(payload.get("analysis_style_id"), 32),
        "low_signal": payload.get("low_signal") is True,
        "synthetic": payload.get("synthetic") is True,
        "client_timestamp": _safe_client_timestamp(payload.get("client_timestamp")),
        "comment_length": len(comment),
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
        "monitoring_event_type": _safe_monitoring_event_type(payload.get("monitoring_event_type")),
        "client_timestamp": _safe_client_timestamp(payload.get("client_timestamp")),
        "stored_at_unix": round(time(), 3),
        "payload_field_count": len(payload),
        "synthetic": payload.get("synthetic") is True,
    }
    EVENT_ROWS.append(row)
    return row
