"""Optional structured summary layer."""

from __future__ import annotations

from typing import Any, Callable

from ..safety.validator import assert_safe_payload
from ..utils.schema_utils import normalize_summary_payload, safe_json_loads
from .templates import DESCRIPTIVE_SYSTEM_PROMPT


def _deterministic_summary(signals: dict[str, Any]) -> dict[str, Any]:
    what_changed = signals.get("what_changed", {})
    consistency = signals.get("consistency", {})
    shift_radar = signals.get("shift_radar", {})
    confidence = signals.get("confidence_clarity", {})

    observations = []
    for item in what_changed.get("top_changes", [])[:2]:
        observations.append(item)
    for item in consistency.get("top_reasons", [])[:1]:
        observations.append(item)
    strongest = shift_radar.get("shift_start_window") or {}
    if strongest.get("summary"):
        observations.append(str(strongest["summary"]).strip())

    payload = {
        "summary": what_changed.get(
            "comparison_summary",
            "Later and earlier communication windows can be compared through the structured signals.",
        ),
        "observations": observations[:3],
        "limitations": [
            "This summary is descriptive only.",
            "It is based on structured signals rather than raw chat or motive claims.",
            "Optional formatting never replaces the deterministic artifacts.",
        ],
    }
    if confidence:
        payload["limitations"].append(
            "Confidence and clarity signals are strongest in interview-style inputs."
        )
    assert_safe_payload(payload)
    return payload


def rewrite_summary(
    signals: dict[str, Any],
    *,
    rewriter: Callable[[dict[str, Any]], Any] | None = None,
) -> dict[str, Any]:
    fallback = _deterministic_summary(signals)
    if rewriter is None:
        return fallback

    prompt_payload = {
        "system_prompt": DESCRIPTIVE_SYSTEM_PROMPT,
        "signals": signals,
    }
    try:
        raw = rewriter(prompt_payload)
        if isinstance(raw, dict):
            payload = normalize_summary_payload(raw)
        else:
            parsed = safe_json_loads(str(raw))
            payload = normalize_summary_payload(parsed if isinstance(parsed, dict) else {})
        assert_safe_payload(payload)
        return payload
    except Exception:
        return fallback
