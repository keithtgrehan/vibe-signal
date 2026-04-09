"""Confidence and clarity scoring for interview-style responses."""

from __future__ import annotations

import re
from typing import Any

from ..audio.segment_aggregate import aggregate_audio_segments
from ..nlp.sentence_split import sentence_stats
from ..nlp.spacy_features import analyze_spacy_structure
from .shared import average, clamp, punctuation_emphasis_score, safe_excerpt, specificity_score

_SELF_CORRECTION_RE = re.compile(r"\b(sorry|i mean|rather|let me rephrase|no,\s*i|what i meant)\b", re.IGNORECASE)
_RESTART_RE = re.compile(r"\b(um|uh|well|so)\b[\s,]+(?:um|uh|well|so)\b", re.IGNORECASE)
_STRUCTURE_RE = re.compile(r"\b(first|second|third|because|so|for example|the main point|in short|overall)\b", re.IGNORECASE)


def _completeness_score(text: str) -> float:
    stripped = text.strip()
    if not stripped:
        return 0.0
    sentence_info = sentence_stats(stripped)
    score = 0.25
    if stripped.endswith((".", "!", "?")):
        score += 0.25
    if len(stripped.split()) >= 6:
        score += 0.2
    if "because" in stripped.lower() or "so " in stripped.lower():
        score += 0.15
    if "," in stripped:
        score += 0.1
    if int(sentence_info["sentence_count"]) >= 2:
        score += 0.05
    if float(sentence_info["fragment_ratio"]) <= 0.34:
        score += 0.1
    return clamp(score, 0.0, 1.0)


def _structure_score(text: str) -> float:
    structure = analyze_spacy_structure(text)
    score = 0.25
    if _STRUCTURE_RE.search(text):
        score += 0.4
    if text.strip().endswith((".", "!", "?")):
        score += 0.15
    if int(structure.get("explanation_clause_count", 0)) > 0:
        score += 0.12
    if int(structure.get("action_statement_count", 0)) > 0:
        score += 0.08
    if int(structure.get("sentence_count", 0)) >= 2:
        score += 0.05
    score += specificity_score(text) * 0.2
    return clamp(score, 0.0, 1.0)


def _hesitation_explanation(row: dict[str, Any]) -> str:
    reasons: list[str] = []
    if float(row.get("pause_before_answer_ms") or 0.0) >= 450.0:
        reasons.append("longer pause before the segment")
    if float(row.get("filler_density") or 0.0) >= 2.0:
        reasons.append("more filler phrases")
    if int(row.get("self_corrections") or 0) > 0:
        reasons.append("self-correction language")
    if int(row.get("restart_count") or 0) > 0:
        reasons.append("restart-style openings")
    if float(row.get("speech_rate_wpm") or 0.0) and float(row.get("speech_rate_wpm") or 0.0) < 95.0:
        reasons.append("slower delivery")
    if not reasons:
        reasons.append("lighter hesitation markers overall")
    return ", ".join(reasons)


def analyze_confidence_clarity(
    segments: list[dict[str, Any]],
    *,
    segment_metrics: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    metrics = segment_metrics or aggregate_audio_segments(segments)
    if not metrics:
        return {
            "clarity_score": 0.0,
            "confidence_marker_trend": "insufficient_data",
            "strongest_hesitation_segments": [],
            "segment_metrics": [],
        }

    speech_rates = [float(item.get("speech_rate_wpm", 0.0) or 0.0) for item in metrics if float(item.get("speech_rate_wpm", 0.0) or 0.0) > 0]
    baseline_speech_rate = average(speech_rates)
    scored_segments: list[dict[str, Any]] = []
    for row in metrics:
        text = str(row.get("text", ""))
        structure_features = analyze_spacy_structure(text)
        sentence_info = sentence_stats(text)
        self_corrections = max(
            len(_SELF_CORRECTION_RE.findall(text)),
            int(structure_features.get("self_correction_marker_count", 0)),
        )
        restart_count = max(
            len(_RESTART_RE.findall(text)),
            int(structure_features.get("restart_marker_count", 0)),
        )
        completeness = _completeness_score(text)
        structure = _structure_score(text)
        punctuation = punctuation_emphasis_score(text)
        pacing_penalty = 0.0
        speech_rate = float(row.get("speech_rate_wpm", 0.0) or 0.0)
        if baseline_speech_rate and speech_rate:
            pacing_penalty = abs(speech_rate - baseline_speech_rate) / max(baseline_speech_rate, 1.0)
        hesitation = (
            float(row.get("hesitation_score", 0.0) or 0.0)
            + min(self_corrections, 2)
            + min(restart_count, 2)
            + (0.8 if punctuation > 0.55 else 0.0)
        )
        clarity = clamp(
            78.0
            + completeness * 10.0
            + structure * 12.0
            + specificity_score(text) * 8.0
            - hesitation * 8.0
            - (pacing_penalty * 12.0),
            0.0,
            100.0,
        )
        scored_segment = {
            **row,
            "self_corrections": self_corrections,
            "restart_count": restart_count,
            "sentence_completeness": round(completeness, 4),
            "answer_structure": round(structure, 4),
            "sentence_count": int(sentence_info["sentence_count"]),
            "fragment_ratio": round(float(sentence_info["fragment_ratio"]), 4),
            "clarity_score": round(clarity, 2),
            "excerpt": safe_excerpt(text),
        }
        scored_segment["hesitation_explanation"] = _hesitation_explanation(scored_segment)
        scored_segments.append(scored_segment)

    midpoint = max(1, len(scored_segments) // 2)
    early_hesitation = average([float(item["hesitation_score"]) for item in scored_segments[:midpoint]])
    late_hesitation = average([float(item["hesitation_score"]) for item in scored_segments[midpoint:]])
    if late_hesitation > early_hesitation + 0.6:
        trend = "Hesitation markers appear more often in later responses."
    elif early_hesitation > late_hesitation + 0.6:
        trend = "Later responses sound steadier than earlier ones."
    else:
        trend = "Hesitation markers stay relatively even across the responses."

    strongest = sorted(
        scored_segments,
        key=lambda item: (float(item["hesitation_score"]), -float(item["clarity_score"]), int(item["restart_count"])),
        reverse=True,
    )[:3]

    audio_support_segments = [
        item for item in scored_segments if str(item.get("acoustic_support_source", "none")) != "none"
    ]
    optional_audio_support = {
        "available": bool(audio_support_segments),
        "segment_count": len(audio_support_segments),
        "energy_intensity_proxy": round(
            average([float(item.get("acoustic_energy_intensity_proxy", 0.0) or 0.0) for item in audio_support_segments]),
            4,
        )
        if audio_support_segments
        else 0.0,
        "voicing_ratio_proxy": round(
            average([float(item.get("acoustic_voicing_ratio_proxy", 0.0) or 0.0) for item in audio_support_segments]),
            4,
        )
        if audio_support_segments
        else 0.0,
        "pitch_variation_proxy": round(
            average([float(item.get("acoustic_pitch_variation_proxy", 0.0) or 0.0) for item in audio_support_segments]),
            4,
        )
        if audio_support_segments
        else 0.0,
    }

    return {
        "clarity_score": round(average([item["clarity_score"] for item in scored_segments]), 2),
        "confidence_marker_trend": trend,
        "strongest_hesitation_segments": strongest,
        "segment_metrics": scored_segments,
        "optional_audio_support": optional_audio_support,
    }
