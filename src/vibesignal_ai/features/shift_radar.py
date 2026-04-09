"""Conversation shift radar."""

from __future__ import annotations

from typing import Any

from .shared import clamp, compute_boundary_events, normalize_messages, split_windows, window_metrics


def analyze_shift_radar(
    messages: list[dict[str, Any]],
    *,
    turns: list[dict[str, Any]] | None = None,
    segments: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from ..ingest.segmentation import group_turns

    normalized = normalize_messages(messages)
    conversation_turns = turns or group_turns(normalized)
    windows = split_windows(conversation_turns if conversation_turns else normalized)
    if len(windows) < 2:
        return {
            "shift_score": 0.0,
            "strongest_shift_window": None,
            "ranked_contributing_signals": [],
            "window_metrics": [],
            "shift_events": [],
        }

    per_window = []
    for window in windows:
        metrics = window_metrics(window["items"])
        enriched = dict(window)
        enriched["metrics"] = {key: round(value, 4) for key, value in metrics.items()}
        per_window.append(enriched)

    boundary_events = compute_boundary_events(per_window)
    strongest_window = max(boundary_events, key=lambda item: item["shift_value"])
    significant_threshold = 0.16
    first_meaningful = next((item for item in boundary_events if item["shift_value"] >= significant_threshold), strongest_window)

    early_metrics = per_window[0]["metrics"]
    late_metrics = per_window[-1]["metrics"]
    aggregate_contributions = []
    for signal in early_metrics:
        delta = late_metrics[signal] - early_metrics[signal]
        aggregate_contributions.append(
            {
                "signal": signal,
                "delta": round(delta, 4),
                "magnitude": round(abs(delta), 4),
                "summary": strongest_window["top_signals"][0]["summary"] if strongest_window["top_signals"] and strongest_window["top_signals"][0]["signal"] == signal else "",
            }
        )
    ranked = sorted(aggregate_contributions, key=lambda item: item["magnitude"], reverse=True)
    for item in ranked[:]:
        if not item["summary"]:
            for candidate in strongest_window["top_signals"]:
                if candidate["signal"] == item["signal"]:
                    item["summary"] = candidate["summary"]
                    break
        if not item["summary"]:
            item["summary"] = boundary_events[0]["summary"] if boundary_events else "Communication style shifts across the conversation."

    shift_score = average = sum(item["shift_value"] for item in boundary_events) / len(boundary_events)
    return {
        "shift_score": round(clamp(average, 0.0, 1.0) * 100.0, 2),
        "strongest_shift_window": strongest_window,
        "shift_start_window": first_meaningful,
        "ranked_contributing_signals": ranked,
        "window_metrics": per_window,
        "shift_events": boundary_events,
    }
