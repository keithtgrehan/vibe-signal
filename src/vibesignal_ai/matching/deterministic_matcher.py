"""Deterministic communication-fit matcher."""

from __future__ import annotations

import hashlib
from typing import Any

from .confidence import build_confidence
from .contracts import BLOCKED_INTERPRETATIONS, normalize_match_request, validate_match_request, validate_match_result
from .explain import build_factor_lists, build_summary, compact_evidence
from .features import MatchingFeatures, extract_matching_features


POSITIVE_WEIGHTS = {
    "alignment": (0.05, 0.1),
    "consent_clarity": (0.04, 0.08),
    "repair_opportunity": (0.04, 0.08),
    "specificity": (0.035, 0.12),
    "directness": (0.03, 0.08),
    "reassurance": (0.04, 0.08),
    "low_pressure": (0.04, 0.08),
    "boundary_respect": (0.04, 0.08),
}
NEGATIVE_WEIGHTS = {
    "pressure": (0.07, 0.14),
    "boundary_pressure": (0.08, 0.16),
    "escalation_risk": (0.08, 0.16),
    "overloaded_message": (0.05, 0.1),
    "cognitive_load": (0.03, 0.08),
    "ambiguity": (0.045, 0.1),
    "unclear_ask": (0.05, 0.1),
    "specificity_drop": (0.1, 0.2),
    "contradiction_against_prior_message": (0.12, 0.24),
    "unsupported_claim_shift": (0.1, 0.2),
    "answer_evasion_pattern": (0.1, 0.2),
}


def clamp_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def band_for_score(score: float) -> str:
    value = float(score)
    if value < 0.35:
        return "low"
    if value < 0.55:
        return "mixed"
    if value <= 0.75:
        return "moderate"
    return "strong"


def _bounded(count: int, unit: float, cap: float) -> float:
    return min(cap, max(0, int(count)) * unit)


def _score_parts(features: MatchingFeatures) -> tuple[dict[str, float], dict[str, float]]:
    counts = features.cue_counts
    positives = {
        "alignment": _bounded(counts.get("alignment", 0), *POSITIVE_WEIGHTS["alignment"]),
        "consent_clarity": _bounded(counts.get("consent_clarity", 0), *POSITIVE_WEIGHTS["consent_clarity"]),
        "repair": _bounded(counts.get("repair_opportunity", 0), *POSITIVE_WEIGHTS["repair_opportunity"]),
        "specificity": _bounded(counts.get("specificity", 0), *POSITIVE_WEIGHTS["specificity"]),
        "directness": _bounded(counts.get("directness", 0), *POSITIVE_WEIGHTS["directness"]),
        "reassurance": _bounded(counts.get("reassurance", 0), *POSITIVE_WEIGHTS["reassurance"]),
        "low_pressure": _bounded(counts.get("reassurance", 0), *POSITIVE_WEIGHTS["low_pressure"]),
        "boundary_respect": _bounded(features.boundary_respect_count, *POSITIVE_WEIGHTS["boundary_respect"]),
    }
    negatives = {
        "pressure": _bounded(counts.get("pressure", 0), *NEGATIVE_WEIGHTS["pressure"]),
        "boundary_pressure": _bounded(counts.get("boundary_pressure", 0), *NEGATIVE_WEIGHTS["boundary_pressure"]),
        "escalation_risk": _bounded(counts.get("escalation_risk", 0), *NEGATIVE_WEIGHTS["escalation_risk"]),
        "overloaded_message": _bounded(counts.get("overloaded_message", 0), *NEGATIVE_WEIGHTS["overloaded_message"]),
        "cognitive_load": _bounded(counts.get("cognitive_load", 0), *NEGATIVE_WEIGHTS["cognitive_load"]),
        "ambiguity": _bounded(counts.get("ambiguity", 0), *NEGATIVE_WEIGHTS["ambiguity"]),
        "unclear_ask": _bounded(counts.get("unclear_ask", 0), *NEGATIVE_WEIGHTS["unclear_ask"]),
        "specificity_drop": _bounded(counts.get("specificity_drop", 0), *NEGATIVE_WEIGHTS["specificity_drop"]),
        "contradiction": _bounded(counts.get("contradiction_against_prior_message", 0), *NEGATIVE_WEIGHTS["contradiction_against_prior_message"]),
        "unsupported_claim_shift": _bounded(counts.get("unsupported_claim_shift", 0), *NEGATIVE_WEIGHTS["unsupported_claim_shift"]),
        "answer_evasion": _bounded(counts.get("answer_evasion_pattern", 0), *NEGATIVE_WEIGHTS["answer_evasion_pattern"]),
    }
    return positives, negatives


def _match_id(conversation_id: str, messages: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    digest.update(str(conversation_id).encode("utf-8"))
    for message in messages:
        digest.update(str(message.get("id", "")).encode("utf-8"))
        digest.update(str(message.get("author", "")).encode("utf-8"))
        digest.update(str(message.get("text", "")).encode("utf-8"))
    return "vibe_match_" + digest.hexdigest()[:16]


def match_conversation(payload: dict[str, Any]) -> dict[str, Any]:
    """Run deterministic matching and return a safe communication-fit result."""

    errors = validate_match_request(payload)
    if errors:
        raise ValueError("; ".join(errors))

    request = normalize_match_request(payload)
    conversation_id = request["conversation_id"]
    messages = request["messages"]
    features = extract_matching_features(messages, conversation_id=conversation_id)
    positives, negatives = _score_parts(features)
    raw_score = 0.5 + sum(positives.values()) - sum(negatives.values())
    score = clamp_score(raw_score)
    band = band_for_score(score)
    alignment, friction = build_factor_lists(positives, dict(features.cue_counts))
    safe_summary, redline_status, safe_explanation = build_summary(
        band=band,
        score=score,
        alignment=alignment,
        friction=friction,
        override=request.get("debug_summary_override"),
    )

    evidence = compact_evidence(features.all_evidence)
    result = {
        "match_id": _match_id(conversation_id, messages),
        "conversation_id": conversation_id,
        "compatibility_band": band,
        "score": score,
        "confidence": build_confidence(messages, features),
        "top_alignment_factors": alignment,
        "top_friction_factors": friction,
        "positive_factors": alignment,
        "risk_factors": friction,
        "inconsistency_cues": compact_evidence(features.inconsistency_cues),
        "unsupported_claim_shift": compact_evidence(features.unsupported_claim_shift),
        "specificity_drop": compact_evidence(features.specificity_drop),
        "answer_evasion_pattern": compact_evidence(features.answer_evasion_pattern),
        "contradiction_against_prior_message": compact_evidence(features.contradiction_against_prior_message),
        "evidence": evidence,
        "safe_summary": safe_summary,
        "safe_explanation": safe_explanation,
        "redline_status": redline_status,
        "blocked_interpretations": BLOCKED_INTERPRETATIONS,
        "score_components": {
            "base": 0.5,
            "positive": {key: round(value, 4) for key, value in positives.items() if value > 0},
            "negative": {key: round(value, 4) for key, value in negatives.items() if value > 0},
        },
    }
    result_errors = validate_match_result(result)
    if result_errors:
        raise RuntimeError("; ".join(result_errors))
    return result
