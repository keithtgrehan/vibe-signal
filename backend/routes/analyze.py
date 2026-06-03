from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from vibesignal_ai.matching.features import extract_matching_features
from vibesignal_ai.matching.contracts import BLOCKED_INTERPRETATIONS
from vibesignal_ai.safety.validator import validate_payload


router = APIRouter()


@router.post("/api/analyze")
def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    conversation_id = str(payload.get("conversation_id", "manual_backend_analysis"))
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        text = str(payload.get("text", "")).strip()
        if not text:
            raise HTTPException(status_code=400, detail="messages or text is required")
        messages = [{"id": "m1", "author": "unknown", "text": text}]
    errors = validate_payload(messages)
    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))
    features = extract_matching_features(messages, conversation_id=conversation_id)
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
