from __future__ import annotations

import hashlib
from typing import Any


REQUIRED_EVIDENCE_FIELDS = (
    "evidence_id",
    "conversation_id",
    "source_type",
    "message_id",
    "turn_id",
    "speaker_role",
    "cue_name",
    "evidence_text",
    "start_offset",
    "end_offset",
    "text_sha256",
    "provenance",
    "interpretation_limits",
)

REQUIRED_INTERPRETATION_LIMITS = (
    "does_not_infer_true_emotion",
    "does_not_detect_deception",
    "does_not_score_personality",
)

DISALLOWED_EVIDENCE_FIELDS = {
    "emotion_label",
    "deception_score",
    "attraction_score",
    "attachment_style",
    "diagnosis",
    "mental_health_label",
    "manipulation_score",
    "protected_trait_inference",
    "love_prediction",
    "cheating_prediction",
    "intent_label",
}


def stable_text_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def default_interpretation_limits() -> dict[str, bool]:
    return {field: True for field in REQUIRED_INTERPRETATION_LIMITS}


def build_evidence_object(
    *,
    evidence_id: str,
    conversation_id: str,
    source_type: str,
    message_id: str | int,
    turn_id: str | int,
    speaker_role: str,
    cue_name: str,
    evidence_text: str,
    start_offset: int,
    end_offset: int,
    provenance: dict[str, Any],
    interpretation_limits: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = str(evidence_text or "")
    return {
        "evidence_id": str(evidence_id),
        "conversation_id": str(conversation_id),
        "source_type": str(source_type),
        "message_id": str(message_id),
        "turn_id": str(turn_id),
        "speaker_role": str(speaker_role or "unknown"),
        "cue_name": str(cue_name),
        "evidence_text": text,
        "start_offset": int(start_offset),
        "end_offset": int(end_offset),
        "text_sha256": stable_text_hash(text),
        "provenance": dict(provenance or {}),
        "interpretation_limits": dict(interpretation_limits or default_interpretation_limits()),
    }


def _blank(value: Any) -> bool:
    return str(value or "").strip() == ""


def validate_evidence_object(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(row, dict):
        return ["evidence object must be a JSON object"]

    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in row:
            errors.append(f"missing required field {field}")
        elif field not in {"start_offset", "end_offset", "provenance", "interpretation_limits"} and _blank(row.get(field)):
            errors.append(f"required field {field} cannot be empty")

    for field in sorted(DISALLOWED_EVIDENCE_FIELDS):
        if field in row:
            errors.append(f"unsafe field {field} is not allowed")

    start = row.get("start_offset")
    end = row.get("end_offset")
    if not isinstance(start, int) or start < 0:
        errors.append("start_offset must be an integer >= 0")
    if not isinstance(end, int) or end < 0:
        errors.append("end_offset must be an integer >= 0")
    if isinstance(start, int) and isinstance(end, int) and end < start:
        errors.append("end_offset must be >= start_offset")

    text = str(row.get("evidence_text", ""))
    if row.get("text_sha256") != stable_text_hash(text):
        errors.append("text_sha256 does not match evidence_text")

    if not isinstance(row.get("provenance"), dict) or not row.get("provenance"):
        errors.append("provenance must be a non-empty object")

    limits = row.get("interpretation_limits")
    if not isinstance(limits, dict):
        errors.append("interpretation_limits must be an object")
    else:
        for field in REQUIRED_INTERPRETATION_LIMITS:
            if field not in limits:
                errors.append(f"missing interpretation limit {field}")
            elif limits.get(field) is not True:
                errors.append(f"interpretation limit {field} must be true")
    return errors
