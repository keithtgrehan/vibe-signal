"""Analysis-quality confidence for Vibe matching."""

from __future__ import annotations

from typing import Any

from .features import MatchingFeatures


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def build_confidence(messages: list[dict[str, Any]], features: MatchingFeatures) -> dict[str, Any]:
    """Confidence in analysis quality, never in another person's truth or motives."""

    score = 0.95
    reasons: list[str] = []

    if len(messages) < 2 or features.total_word_count < 12:
        score -= 0.25
        reasons.append("Confidence is low because the exchange is short.")
    if features.one_sided:
        score -= 0.2
        reasons.append("Confidence is lower because the exchange is one-sided.")
    if features.missing_timestamp_count:
        score -= 0.15
        reasons.append("Confidence is lower because timestamps are missing from one or more messages.")
    if len(features.all_evidence) < 3:
        score -= 0.15
        reasons.append("Confidence is lower because there are few evidence-backed cues.")
    if features.vague_message_count:
        score -= min(0.15, 0.05 * features.vague_message_count)
        reasons.append("Confidence is lower because vague wording limits stable analysis.")
    if features.cue_counts.get("ambiguity", 0) or features.cue_counts.get("unclear_ask", 0):
        score -= 0.1
        reasons.append("Confidence is lower because ambiguity cues are present.")
    if features.contradiction_against_prior_message and len(features.contradiction_against_prior_message) == 1:
        score -= 0.05
        reasons.append("Contradiction confidence is limited to deterministic pattern-level evidence.")

    score = round(_clamp(score), 2)
    if score >= 0.75:
        level = "high"
    elif score >= 0.55:
        level = "medium"
    else:
        level = "low"

    if not reasons:
        reasons.append("Confidence is higher because both sides have enough evidence-backed cues for this deterministic analysis.")

    return {"level": level, "score": score, "reasons": reasons}
