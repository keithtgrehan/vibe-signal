"""Directness feature helpers."""

from __future__ import annotations

from typing import Any

from .shared import average, directness_score, normalize_messages


def analyze_directness(messages: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = normalize_messages(messages)
    scores = [
        {
            "message_id": item["message_id"],
            "speaker": item["speaker"],
            "score": round(directness_score(item["text"]), 4),
        }
        for item in normalized
        if not item["is_system"]
    ]
    return {
        "overall_score": round(average([item["score"] for item in scores]), 4),
        "message_scores": scores,
    }
