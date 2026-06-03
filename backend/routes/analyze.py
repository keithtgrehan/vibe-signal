from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from vibesignal_ai.features.cue_taxonomy import detect_cues
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
    evidence = detect_cues(messages, conversation_id=conversation_id)
    signal_state = "ready" if evidence else "low_signal"
    return {
        "conversation_id": conversation_id,
        "analysis_mode": "deterministic_local_only",
        "analysis_quality": "cue_evidence_only",
        "signal_state": signal_state,
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
