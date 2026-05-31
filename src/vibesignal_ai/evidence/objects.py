from __future__ import annotations

import hashlib
import re
from typing import Any


REQUIRED_EVIDENCE_FIELDS = (
    "evidence_id",
    "conversation_id",
    "source_type",
    "message_id",
    "turn_id",
    "speaker_role",
    "cue_name",
    "cue_id",
    "cue_family",
    "evidence_text",
    "start_offset",
    "end_offset",
    "span_start",
    "span_end",
    "confidence",
    "explanation",
    "safe_phrase",
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
SAFE_PHRASE_PREFIXES = ("message contains", "text cues suggest")
FORBIDDEN_GENERATED_LANGUAGE = (
    r"\bthey feel\b",
    r"\bthe person feels\b",
    r"\bthe person is\b",
    r"\bdiagnos",
    r"\battachment style\b",
    r"\bmake them like you\b",
    r"\bpersuasion optimization\b",
    r"\btrue emotion\b",
    r"\bmanipulation\b",
)
FAMILY_PREFIXES = {
    "directness",
    "specificity",
    "hedging",
    "urgency",
    "reassurance",
    "pressure",
    "conflict",
    "alignment",
    "response_timing",
    "topic_shift",
    "ambiguity",
    "cognitive_load",
    "unclear_ask",
    "overloaded_message",
    "escalation_risk",
    "repair_opportunity",
    "boundary_pressure",
    "consent_clarity",
}


def stable_text_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def default_interpretation_limits() -> dict[str, bool]:
    return {field: True for field in REQUIRED_INTERPRETATION_LIMITS}


def infer_cue_family(cue_name: str) -> str:
    cue = str(cue_name or "").strip()
    if cue in FAMILY_PREFIXES:
        return cue
    for family in sorted(FAMILY_PREFIXES, key=len, reverse=True):
        if cue.startswith(family):
            return family
    return "legacy"


def default_safe_phrase(cue_family: str) -> str:
    normalized = str(cue_family or "legacy").replace("_", "-")
    return f"message contains {normalized} cue wording."


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
    cue_id: str | None = None,
    cue_family: str | None = None,
    span_start: int | None = None,
    span_end: int | None = None,
    confidence: float = 0.5,
    explanation: str | None = None,
    safe_phrase: str | None = None,
) -> dict[str, Any]:
    text = str(evidence_text or "")
    cue = str(cue_id or cue_name)
    family = str(cue_family or infer_cue_family(cue))
    start = int(start_offset if span_start is None else span_start)
    end = int(end_offset if span_end is None else span_end)
    return {
        "evidence_id": str(evidence_id),
        "conversation_id": str(conversation_id),
        "source_type": str(source_type),
        "message_id": str(message_id),
        "turn_id": str(turn_id),
        "speaker_role": str(speaker_role or "unknown"),
        "cue_name": str(cue_name),
        "cue_id": cue,
        "cue_family": family,
        "evidence_text": text,
        "start_offset": int(start_offset),
        "end_offset": int(end_offset),
        "span_start": start,
        "span_end": end,
        "confidence": float(confidence),
        "explanation": str(explanation or f"Deterministic rule matched {family.replace('_', ' ')} wording."),
        "safe_phrase": str(safe_phrase or default_safe_phrase(family)),
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
        elif field not in {"start_offset", "end_offset", "span_start", "span_end", "confidence", "provenance", "interpretation_limits"} and _blank(row.get(field)):
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

    span_start = row.get("span_start")
    span_end = row.get("span_end")
    if not isinstance(span_start, int) or span_start < 0:
        errors.append("span_start must be an integer >= 0")
    if not isinstance(span_end, int) or span_end < 0:
        errors.append("span_end must be an integer >= 0")
    if isinstance(span_start, int) and isinstance(span_end, int) and span_end < span_start:
        errors.append("span_end must be >= span_start")
    if isinstance(start, int) and isinstance(span_start, int) and span_start != start:
        errors.append("span_start must match start_offset")
    if isinstance(end, int) and isinstance(span_end, int) and span_end != end:
        errors.append("span_end must match end_offset")

    confidence = row.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= float(confidence) <= 1:
        errors.append("confidence must be a number between 0 and 1")

    text = str(row.get("evidence_text", ""))
    if row.get("text_sha256") != stable_text_hash(text):
        errors.append("text_sha256 does not match evidence_text")

    safe_phrase = str(row.get("safe_phrase", ""))
    if not safe_phrase.lower().startswith(SAFE_PHRASE_PREFIXES):
        errors.append("safe_phrase must start with safe cue wording")
    for field in ("safe_phrase", "explanation"):
        generated = str(row.get(field, ""))
        for pattern in FORBIDDEN_GENERATED_LANGUAGE:
            if re.search(pattern, generated, re.IGNORECASE):
                errors.append(f"{field} contains forbidden interpretive language: {pattern}")

    if row.get("raw_text_commit_allowed") is True and row.get("rights_tier") in {"restricted", "unknown"}:
        errors.append("restricted or unknown rights cannot allow raw text commit")
    if row.get("raw_text_commit_allowed") is True and row.get("commit_allowed") is not True:
        errors.append("raw_text_commit_allowed requires commit_allowed")

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
