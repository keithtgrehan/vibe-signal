from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from ..storage import store_event_metadata


router = APIRouter()


def _accept_event(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "accepted",
        "event_type": event_type,
        "raw_payload_persisted": False,
        "stored_event": store_event_metadata(event_type, payload),
    }


@router.post("/api/events/analysis")
def analysis_event(payload: dict[str, Any]) -> dict[str, Any]:
    return _accept_event("analysis", payload)


@router.post("/api/events/quota")
def quota_event(payload: dict[str, Any]) -> dict[str, Any]:
    return _accept_event("quota", payload)


@router.post("/api/events/billing")
def billing_event(payload: dict[str, Any]) -> dict[str, Any]:
    return _accept_event("billing", payload)


@router.post("/api/events/state")
def state_event(payload: dict[str, Any]) -> dict[str, Any]:
    return _accept_event("state", payload)
