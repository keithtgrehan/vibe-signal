"""UI payload builders for safe comparison cards."""

from __future__ import annotations

from typing import Any

from ..safety.validator import assert_safe_payload


def _metric(label: str, value: Any) -> dict[str, Any]:
    return {"label": label, "value": value}


def build_pattern_summary_card(
    shift_radar: dict[str, Any],
    consistency: dict[str, Any],
    confidence_clarity: dict[str, Any],
    what_changed: dict[str, Any],
) -> dict[str, Any]:
    top_changes = what_changed.get("top_changes", [])[:2]
    top_reason = consistency.get("top_reasons", [])[:1]
    headline = what_changed.get(
        "comparison_summary",
        "Later and earlier communication windows can be compared through the structured signals.",
    )
    payload = {
        "card_id": "pattern_summary",
        "title": "Pattern Summary",
        "headline": headline,
        "bullets": top_changes + top_reason,
        "metrics": [
            _metric("Shift score", shift_radar.get("shift_score", 0)),
            _metric("Consistency", consistency.get("consistency_level", "n/a")),
            _metric("Clarity score", confidence_clarity.get("clarity_score", 0)),
        ],
    }
    assert_safe_payload(payload)
    return payload


def build_shift_radar_card(shift_radar: dict[str, Any]) -> dict[str, Any]:
    strongest = shift_radar.get("strongest_shift_window") or {}
    payload = {
        "card_id": "conversation_shift_radar",
        "title": "Conversation Shift Radar",
        "headline": strongest.get(
            "summary",
            "A meaningful communication shift appears across the later windows.",
        ),
        "bullets": [item["summary"] for item in shift_radar.get("ranked_contributing_signals", [])[:3]],
        "metrics": [
            _metric("Shift score", shift_radar.get("shift_score", 0)),
            _metric("Change starts", strongest.get("change_starts_at_turn_id", "n/a")),
        ],
    }
    assert_safe_payload(payload)
    return payload


def build_consistency_card(consistency: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "card_id": "response_consistency",
        "title": "Response Consistency Check",
        "headline": (
            "Direct answer style, topic alignment, and detail continuity can be compared across linked responses."
        ),
        "bullets": consistency.get("top_reasons", [])[:3],
        "metrics": [
            _metric("Consistency level", consistency.get("consistency_level", "n/a")),
            _metric("Consistency score", consistency.get("consistency_score", 0)),
        ],
        "evidence": consistency.get("supporting_spans", [])[:3],
    }
    assert_safe_payload(payload)
    return payload


def build_confidence_card(confidence_clarity: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "card_id": "confidence_clarity",
        "title": "Confidence & Clarity",
        "headline": "Hesitation, restart, pacing, and structure markers can be compared across the interview segments.",
        "bullets": [confidence_clarity.get("confidence_marker_trend", "No trend available.")],
        "metrics": [
            _metric("Clarity score", confidence_clarity.get("clarity_score", 0)),
        ],
        "evidence": confidence_clarity.get("strongest_hesitation_segments", [])[:3],
    }
    assert_safe_payload(payload)
    return payload


def build_what_changed_card(what_changed: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "card_id": "what_changed",
        "title": "What Changed?",
        "headline": what_changed.get(
            "comparison_summary",
            "Earlier and later windows can be compared for communication changes.",
        ),
        "bullets": what_changed.get("top_changes", [])[:3],
        "metrics": [
            _metric(
                "Earliest shift point",
                what_changed.get("earliest_significant_shift_point", "n/a"),
            )
        ],
        "ranked_deltas": what_changed.get("ranked_deltas", [])[:5],
    }
    assert_safe_payload(payload)
    return payload


def build_ui_summary(
    pattern_summary: dict[str, Any],
    shift_card: dict[str, Any],
    consistency_card: dict[str, Any],
    confidence_card: dict[str, Any],
    what_changed_card: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "title": "UI Summary",
        "headline": pattern_summary["headline"],
        "bullets": pattern_summary.get("bullets", [])[:2] + [shift_card["headline"]],
        "cards": [
            {"card_id": pattern_summary["card_id"], "title": pattern_summary["title"], "headline": pattern_summary["headline"]},
            {"card_id": shift_card["card_id"], "title": shift_card["title"], "headline": shift_card["headline"]},
            {"card_id": consistency_card["card_id"], "title": consistency_card["title"], "headline": consistency_card["headline"]},
            {"card_id": confidence_card["card_id"], "title": confidence_card["title"], "headline": confidence_card["headline"]},
            {"card_id": what_changed_card["card_id"], "title": what_changed_card["title"], "headline": what_changed_card["headline"]},
        ],
    }
    assert_safe_payload(payload)
    return payload


def build_payloads(
    *,
    shift_radar: dict[str, Any],
    consistency: dict[str, Any],
    confidence_clarity: dict[str, Any],
    what_changed: dict[str, Any],
) -> dict[str, Any]:
    pattern_summary = build_pattern_summary_card(
        shift_radar, consistency, confidence_clarity, what_changed
    )
    shift_card = build_shift_radar_card(shift_radar)
    consistency_card = build_consistency_card(consistency)
    confidence_card = build_confidence_card(confidence_clarity)
    what_changed_card = build_what_changed_card(what_changed)
    payload = {
        "pattern_summary": pattern_summary,
        "conversation_shift_radar": shift_card,
        "response_consistency": consistency_card,
        "confidence_clarity": confidence_card,
        "what_changed": what_changed_card,
        "ui_summary": build_ui_summary(
            pattern_summary,
            shift_card,
            consistency_card,
            confidence_card,
            what_changed_card,
        ),
    }
    assert_safe_payload(payload)
    return payload
