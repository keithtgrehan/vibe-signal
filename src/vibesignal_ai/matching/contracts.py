"""Contracts for deterministic Vibe communication-fit matching."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..safety.redline_output_blocker import check_output_text
from ..safety.validator import validate_text


ALLOWED_AUTHORS = {"self", "other", "unknown"}
ALLOWED_MESSAGE_LOAD = {"low", "medium", "high"}
ALLOWED_BANDS = {"low", "mixed", "moderate", "strong"}
ALLOWED_CONFIDENCE_LEVELS = {"low", "medium", "high"}
ALLOWED_REDLINE_STATUS = {"allow", "block"}
BLOCKED_INTERPRETATIONS = [
    "deception",
    "hidden_intent",
    "attraction",
    "cheating",
    "diagnosis",
    "neurotype",
    "attachment_style",
    "manipulation",
    "emotional_truth",
]
RESULT_ARRAY_FIELDS = (
    "top_alignment_factors",
    "top_friction_factors",
    "positive_factors",
    "risk_factors",
    "inconsistency_cues",
    "unsupported_claim_shift",
    "specificity_drop",
    "answer_evasion_pattern",
    "contradiction_against_prior_message",
    "evidence",
    "blocked_interpretations",
)
RESULT_REQUIRED_FIELDS = (
    "match_id",
    "conversation_id",
    "compatibility_band",
    "score",
    "confidence",
    "top_alignment_factors",
    "top_friction_factors",
    "positive_factors",
    "risk_factors",
    "inconsistency_cues",
    "unsupported_claim_shift",
    "specificity_drop",
    "answer_evasion_pattern",
    "contradiction_against_prior_message",
    "evidence",
    "safe_summary",
    "safe_explanation",
    "redline_status",
    "blocked_interpretations",
)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _iso_datetime_or_empty(value: Any) -> bool:
    if value in (None, ""):
        return True
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_match_request(payload: Any) -> list[str]:
    """Return human-readable validation errors for a match request."""

    if not isinstance(payload, dict):
        return ["match request must be a JSON object"]

    errors: list[str] = []
    if not _non_empty_string(payload.get("conversation_id")):
        errors.append("conversation_id must be a non-empty string")

    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        errors.append("messages must be a non-empty list")
    elif not all(isinstance(message, dict) for message in messages):
        errors.append("messages must contain only JSON objects")
    else:
        for index, message in enumerate(messages):
            prefix = f"messages[{index}]"
            if not _non_empty_string(message.get("id")):
                errors.append(f"{prefix}.id must be a non-empty string")
            author = str(message.get("author", "")).strip()
            if author not in ALLOWED_AUTHORS:
                errors.append(f"{prefix}.author must be one of {sorted(ALLOWED_AUTHORS)}")
            if not _non_empty_string(message.get("text")):
                errors.append(f"{prefix}.text must be a non-empty string")
            if not _iso_datetime_or_empty(message.get("created_at")):
                errors.append(f"{prefix}.created_at must be an ISO-8601 string when provided")

    preferences = payload.get("user_preferences", {})
    if preferences is None:
        preferences = {}
    if not isinstance(preferences, dict):
        errors.append("user_preferences must be a JSON object when provided")
    else:
        for key in ("prefers_directness", "prefers_low_pressure", "prefers_explicit_plans"):
            if key in preferences and not isinstance(preferences[key], bool):
                errors.append(f"user_preferences.{key} must be a boolean")
        if "max_message_load" in preferences and preferences["max_message_load"] not in ALLOWED_MESSAGE_LOAD:
            errors.append(f"user_preferences.max_message_load must be one of {sorted(ALLOWED_MESSAGE_LOAD)}")

    return errors


def normalize_match_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize request shape while keeping raw text unchanged."""

    errors = validate_match_request(payload)
    if errors:
        raise ValueError("; ".join(errors))

    preferences = dict(payload.get("user_preferences") or {})
    normalized_preferences = {
        "prefers_directness": bool(preferences.get("prefers_directness", False)),
        "prefers_low_pressure": bool(preferences.get("prefers_low_pressure", False)),
        "prefers_explicit_plans": bool(preferences.get("prefers_explicit_plans", False)),
        "max_message_load": str(preferences.get("max_message_load", "medium")),
    }

    messages: list[dict[str, Any]] = []
    for message in payload["messages"]:
        author = str(message.get("author") or "unknown").strip()
        normalized = {
            "id": str(message["id"]).strip(),
            "message_id": str(message["id"]).strip(),
            "turn_id": str(message.get("turn_id", message["id"])).strip(),
            "author": author,
            "speaker_role": author,
            "text": str(message["text"]),
        }
        if message.get("created_at"):
            normalized["created_at"] = str(message["created_at"]).strip()
        messages.append(normalized)

    result = {
        "conversation_id": str(payload["conversation_id"]).strip(),
        "messages": messages,
        "user_preferences": normalized_preferences,
    }
    if payload.get("debug_summary_override"):
        result["debug_summary_override"] = str(payload["debug_summary_override"])
    return result


def _validate_factor_texts(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("safe_summary", "safe_explanation"):
        value = str(result.get(field, ""))
        errors.extend(validate_text(value, field_name=field))
        if check_output_text(value)["status"] == "block":
            errors.append(f"{field} failed red-line output validation")
    for field in ("top_alignment_factors", "top_friction_factors", "positive_factors", "risk_factors"):
        for index, value in enumerate(result.get(field, []) or []):
            errors.extend(validate_text(str(value), field_name=f"{field}[{index}]"))
    for field in (
        "inconsistency_cues",
        "unsupported_claim_shift",
        "specificity_drop",
        "answer_evasion_pattern",
        "contradiction_against_prior_message",
        "evidence",
    ):
        for index, item in enumerate(result.get(field, []) or []):
            if not isinstance(item, dict):
                continue
            for generated_field in ("safe_phrase", "explanation"):
                value = item.get(generated_field)
                if value is None:
                    continue
                field_name = f"{field}[{index}].{generated_field}"
                errors.extend(validate_text(str(value), field_name=field_name))
                if check_output_text(str(value))["status"] == "block":
                    errors.append(f"{field_name} failed red-line output validation")
    return errors


def validate_match_result(payload: Any) -> list[str]:
    """Return validation errors for deterministic match results."""

    if not isinstance(payload, dict):
        return ["match result must be a JSON object"]

    errors: list[str] = []
    for field in RESULT_REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing required field {field}")
    if errors:
        return errors

    if not _non_empty_string(payload.get("match_id")):
        errors.append("match_id must be a non-empty string")
    if not _non_empty_string(payload.get("conversation_id")):
        errors.append("conversation_id must be a non-empty string")
    if payload.get("compatibility_band") not in ALLOWED_BANDS:
        errors.append(f"compatibility_band must be one of {sorted(ALLOWED_BANDS)}")
    score = payload.get("score")
    if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0.0 <= float(score) <= 1.0:
        errors.append("score must be a number between 0.0 and 1.0")

    confidence = payload.get("confidence")
    if not isinstance(confidence, dict):
        errors.append("confidence must be a JSON object")
    else:
        if confidence.get("level") not in ALLOWED_CONFIDENCE_LEVELS:
            errors.append(f"confidence.level must be one of {sorted(ALLOWED_CONFIDENCE_LEVELS)}")
        confidence_score = confidence.get("score")
        if not isinstance(confidence_score, (int, float)) or isinstance(confidence_score, bool) or not 0.0 <= float(confidence_score) <= 1.0:
            errors.append("confidence.score must be a number between 0.0 and 1.0")
        if not isinstance(confidence.get("reasons"), list):
            errors.append("confidence.reasons must be a list")

    for field in RESULT_ARRAY_FIELDS:
        if not isinstance(payload.get(field), list):
            errors.append(f"{field} must be a list")

    for field in (
        "inconsistency_cues",
        "unsupported_claim_shift",
        "specificity_drop",
        "answer_evasion_pattern",
        "contradiction_against_prior_message",
        "evidence",
    ):
        for index, item in enumerate(payload.get(field, []) or []):
            if not isinstance(item, dict):
                errors.append(f"{field}[{index}] must be a JSON object")
                continue
            if not _non_empty_string(item.get("evidence_id")):
                errors.append(f"{field}[{index}].evidence_id must be a non-empty string")
            if not _non_empty_string(item.get("evidence_text")):
                errors.append(f"{field}[{index}].evidence_text must be a non-empty string")

    if payload.get("redline_status") not in ALLOWED_REDLINE_STATUS:
        errors.append(f"redline_status must be one of {sorted(ALLOWED_REDLINE_STATUS)}")
    if payload.get("blocked_interpretations") != BLOCKED_INTERPRETATIONS:
        errors.append("blocked_interpretations must match the Vibe matching red-line list")

    errors.extend(_validate_factor_texts(payload))
    return errors
