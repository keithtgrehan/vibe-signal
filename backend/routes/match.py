from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from vibesignal_ai.matching import match_conversation
from vibesignal_ai.matching.contracts import validate_match_request


router = APIRouter()


@router.post("/api/match")
def create_match(payload: dict[str, Any]) -> dict[str, Any]:
    errors = validate_match_request(payload)
    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))
    try:
        return match_conversation(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="match request could not be processed safely") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail="match service unavailable") from exc
