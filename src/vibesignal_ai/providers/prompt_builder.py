"""Prompt construction for optional external provider summaries."""

from __future__ import annotations

import json
from typing import Any

from .models import ProviderPromptPayload

PROVIDER_SYSTEM_PROMPT = """You are generating a short descriptive-only summary for a communication-pattern analysis tool.

Rules:
- Use the structured signals as the primary source of truth.
- Optional excerpt text may be referenced only as supporting context.
- Do not claim truth, deception, fidelity, motive, intent, diagnosis, or interview outcome.
- Do not give advice.
- Do not use verdict framing.
- Do not say "they are ..." in a conclusive way.
- Keep the summary neutral, comparison-based, and observational.
- Return JSON with exactly one key: output_text.
"""


def _signal_bundle(signals: dict[str, Any]) -> dict[str, Any]:
    shift = signals.get("shift_radar", {})
    consistency = signals.get("consistency", {})
    clarity = signals.get("confidence_clarity", {})
    changed = signals.get("what_changed", {})
    return {
        "shift_radar": {
            "shift_score": shift.get("shift_score", 0),
            "strongest_shift_window": (shift.get("strongest_shift_window") or {}).get("summary", ""),
            "ranked_contributing_signals": [
                item.get("summary", "")
                for item in shift.get("ranked_contributing_signals", [])[:3]
            ],
        },
        "response_consistency": {
            "consistency_level": consistency.get("consistency_level", "n/a"),
            "consistency_score": consistency.get("consistency_score", 0),
            "top_reasons": consistency.get("top_reasons", [])[:3],
        },
        "confidence_clarity": {
            "clarity_score": clarity.get("clarity_score", 0),
            "confidence_marker_trend": clarity.get("confidence_marker_trend", ""),
        },
        "what_changed": {
            "comparison_summary": changed.get("comparison_summary", ""),
            "top_changes": changed.get("top_changes", [])[:3],
        },
    }


def build_provider_prompt(
    *,
    provider_name: str,
    signals: dict[str, Any],
    selected_excerpts: list[str] | None = None,
) -> ProviderPromptPayload:
    cleaned_excerpts = [
        " ".join(str(item or "").split()).strip()
        for item in (selected_excerpts or [])
        if str(item or "").strip()
    ][:4]
    content_source = "signals_plus_excerpt" if cleaned_excerpts else "signals_only"
    signal_bundle = _signal_bundle(signals)
    user_payload: dict[str, Any] = {
        "task": "Write a short descriptive summary of the communication-pattern signals.",
        "content_source": content_source,
        "signals": signal_bundle,
    }
    if cleaned_excerpts:
        user_payload["selected_excerpts"] = cleaned_excerpts

    return ProviderPromptPayload(
        provider_name=str(provider_name or "").strip().lower(),
        system_prompt=PROVIDER_SYSTEM_PROMPT,
        user_prompt=json.dumps(user_payload, ensure_ascii=True, indent=2),
        content_source=content_source,
        signal_bundle=signal_bundle,
        selected_excerpts=cleaned_excerpts,
    )
