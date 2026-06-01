from __future__ import annotations

from typing import Any


def require_json_object(payload: Any, route_name: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{route_name} payload must be a JSON object")
    return payload
