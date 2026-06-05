from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from vibesignal_ai.matching.features import extract_matching_features
from vibesignal_ai.matching.contracts import ALLOWED_AUTHORS, BLOCKED_INTERPRETATIONS
from vibesignal_ai.safety.validator import validate_payload


router = APIRouter()
MAX_ANALYZE_TEXT_CHARS = 2000
ANALYZE_INPUT_LIMIT_DETAIL = (
    "This beta works best with short excerpts. Try 2-8 messages or under 2,000 characters."
)


def _coerce_messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        text = str(payload.get("text", "")).strip()
        if not text:
            raise HTTPException(status_code=400, detail="messages or text is required")
        messages = [{"id": "m1", "author": "unknown", "text": text}]
    if not all(isinstance(message, dict) for message in messages):
        raise HTTPException(status_code=400, detail="messages must contain only JSON objects")
    return messages


def _validate_messages(messages: list[dict[str, Any]]) -> None:
    total_text_chars = 0
    has_text = False
    for message in messages:
        text = str(message.get("text", "")).strip()
        author = str(message.get("author", "unknown")).strip() or "unknown"
        if author not in ALLOWED_AUTHORS:
            raise HTTPException(status_code=400, detail="message author is not supported")
        if text:
            has_text = True
        total_text_chars += len(text)
    if not has_text:
        raise HTTPException(status_code=400, detail="messages must include non-empty text")
    if total_text_chars > MAX_ANALYZE_TEXT_CHARS:
        raise HTTPException(status_code=400, detail=ANALYZE_INPUT_LIMIT_DETAIL)


@router.post("/api/analyze")
def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        conversation_id = str(payload.get("conversation_id", "manual_backend_analysis"))
        messages = _coerce_messages(payload)
        _validate_messages(messages)
        errors = validate_payload(messages)
        if errors:
            raise HTTPException(status_code=400, detail="; ".join(errors))
        features = extract_matching_features(messages, conversation_id=conversation_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="analyze request could not be processed safely") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail="analyze service unavailable") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="analyze service unavailable") from exc

    evidence = features.all_evidence
    signal_state = "ready" if evidence and features.total_word_count >= 10 else "low_signal"
    signal_strength = "low" if signal_state == "ready" else "insufficient"
    return {
        "conversation_id": conversation_id,
        "analysis_mode": "deterministic_local_only",
        "analysis_quality": "cue_evidence_only",
        "signal_state": signal_state,
        "signal_strength": signal_strength,
        "low_signal_fallback": signal_state == "low_signal",
        "provider_used": False,
        "raw_chat_persisted": False,
        "safe_summary": "Cue evidence only; no fit, motive, deception, or emotional-state estimate.",
        "blocked_interpretations": BLOCKED_INTERPRETATIONS,
        "cannot_infer": [
            "private feelings or motives",
            "deception verdicts or private context not present in the text",
            "clinical, neurodevelopmental, personality, relationship-style, or identity labels",
            "relationship outcomes",
        ],
        "evidence": evidence,
    }
