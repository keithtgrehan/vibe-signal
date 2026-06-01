from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from ..storage import store_feedback_metadata


router = APIRouter()


@router.post("/api/feedback")
def create_feedback(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("consent_to_store_feedback") is not True:
        raise HTTPException(status_code=400, detail="Feedback storage requires explicit consent.")
    if not str(payload.get("match_id", "")).strip():
        raise HTTPException(status_code=400, detail="match_id is required")
    return {
        "status": "accepted",
        "raw_comment_persisted": False,
        "stored_feedback": store_feedback_metadata(payload),
    }
