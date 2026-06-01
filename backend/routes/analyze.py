from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from vibesignal_ai.features.cue_taxonomy import detect_cues
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
    return {
        "conversation_id": conversation_id,
        "analysis_mode": "deterministic_local_only",
        "provider_used": False,
        "raw_chat_persisted": False,
        "evidence": detect_cues(messages, conversation_id=conversation_id),
    }
