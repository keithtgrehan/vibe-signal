"""Ranked earlier-vs-later comparison output."""

from __future__ import annotations

from typing import Any

from .shared import compute_boundary_events, normalize_messages, signal_summary, split_windows, window_metrics


def analyze_what_changed(
    messages: list[dict[str, Any]],
    *,
    turns: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from ..ingest.segmentation import group_turns

    normalized = normalize_messages(messages)
    conversation_turns = turns or group_turns(normalized)
    windows = split_windows(conversation_turns if conversation_turns else normalized)
    if len(windows) < 2:
        return {
            "top_changes": [],
            "earliest_significant_shift_point": None,
            "comparison_summary": "Not enough content was available to compare earlier and later windows.",
            "ranked_deltas": [],
            "boundary_events": [],
        }

    enriched = []
    for window in windows:
        row = dict(window)
        row["metrics"] = {key: round(value, 4) for key, value in window_metrics(window["items"]).items()}
        enriched.append(row)

    boundary_events = compute_boundary_events(enriched)
    threshold = 0.16
    earliest_event = next((event for event in boundary_events if event["shift_value"] >= threshold), None)
    strongest_event = max(boundary_events, key=lambda item: item["shift_value"])

    early_metrics = enriched[0]["metrics"]
    late_metrics = enriched[-1]["metrics"]
    ranked_deltas = sorted(
        [
            {
                "signal": signal,
                "delta": round(late_metrics[signal] - early_metrics[signal], 4),
                "magnitude": round(abs(late_metrics[signal] - early_metrics[signal]), 4),
                "summary": signal_summary(signal, late_metrics[signal] - early_metrics[signal]),
            }
            for signal in early_metrics
        ],
        key=lambda item: item["magnitude"],
        reverse=True,
    )
    top_changes = [item["summary"] for item in strongest_event["top_signals"][:3]]
    if not top_changes:
        top_changes = [item["summary"] for item in ranked_deltas[:3]]
    comparison_summary = " ".join(item["summary"] for item in strongest_event["top_signals"][:2]).strip()
    return {
        "top_changes": top_changes,
        "earliest_significant_shift_point": earliest_event["change_starts_at_turn_id"] if earliest_event else None,
        "comparison_summary": comparison_summary or "Communication patterns look broadly similar across the sampled windows.",
        "ranked_deltas": ranked_deltas,
        "boundary_events": boundary_events,
    }
