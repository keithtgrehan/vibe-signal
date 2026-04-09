"""Hedging feature helpers."""

from __future__ import annotations

from typing import Any

from .shared import average, hedge_count, hedging_density, normalize_messages


def analyze_hedging(messages: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = normalize_messages(messages)
    rows = [
        {
            "message_id": item["message_id"],
            "speaker": item["speaker"],
            "hedge_count": hedge_count(item["text"]),
            "density": round(hedging_density(item["text"]), 4),
        }
        for item in normalized
        if not item["is_system"]
    ]
    return {
        "overall_density": round(average([item["density"] for item in rows]), 4),
        "message_scores": rows,
    }
