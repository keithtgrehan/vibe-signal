"""Specificity feature helpers."""

from __future__ import annotations

from typing import Any

from .shared import average, normalize_messages, specificity_score


def analyze_specificity(messages: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = normalize_messages(messages)
    scores = [
        {
            "message_id": item["message_id"],
            "speaker": item["speaker"],
            "score": round(specificity_score(item["text"]), 4),
        }
        for item in normalized
        if not item["is_system"]
    ]
    return {
        "overall_score": round(average([item["score"] for item in scores]), 4),
        "message_scores": scores,
    }
