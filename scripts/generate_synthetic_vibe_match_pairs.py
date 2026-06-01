#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FEATURE_KEYS = (
    "clarity_fit",
    "boundary_fit",
    "repair_fit",
    "communication_fit",
    "pressure_risk",
    "cognitive_load_fit",
    "inconsistency_cues",
    "unsupported_claim_shift",
    "specificity_drop",
    "answer_evasion_pattern",
    "contradiction_against_prior_message",
)
BLOCKED_INTERPRETATIONS = ["deception", "attraction", "diagnosis", "hidden_intent"]


def features(**overrides: int) -> dict[str, int]:
    row = {key: 0 for key in FEATURE_KEYS}
    row.update(overrides)
    return row


SCENARIOS: list[dict[str, Any]] = [
    {
        "category": "strong_fit",
        "text_a": "Can you confirm Friday at 3pm?",
        "text_b": "Yes, Friday at 3pm works. No pressure if we need to adjust.",
        "label": "communication_fit",
        "label_value": 1,
        "evidence": ["Both messages use a specific time and the reply directly confirms the ask."],
        "features": features(clarity_fit=1, boundary_fit=1, communication_fit=1, cognitive_load_fit=1),
    },
    {
        "category": "moderate_fit",
        "text_a": "Could we decide by Thursday?",
        "text_b": "Thursday should work; I may need to confirm the exact time.",
        "label": "communication_fit",
        "label_value": 1,
        "evidence": ["The reply tracks the ask but leaves one detail open."],
        "features": features(clarity_fit=1, communication_fit=1, cognitive_load_fit=1),
    },
    {
        "category": "mixed_fit",
        "text_a": "Can you send the plan before noon?",
        "text_b": "Maybe later; I can send part of it tonight.",
        "label": "communication_fit",
        "label_value": 0,
        "evidence": ["The reply includes a partial plan but softens the requested deadline."],
        "features": features(clarity_fit=1, communication_fit=0, cognitive_load_fit=1, specificity_drop=1),
    },
    {
        "category": "low_fit",
        "text_a": "Can you confirm the time?",
        "text_b": "Whatever, this is too much right now.",
        "label": "communication_fit",
        "label_value": 0,
        "evidence": ["The reply does not confirm the requested time."],
        "features": features(communication_fit=0, pressure_risk=1, answer_evasion_pattern=1),
    },
    {
        "category": "high_pressure",
        "text_a": "Can we choose a calmer time to discuss this?",
        "text_b": "You have to answer right now.",
        "label": "pressure_risk",
        "label_value": 1,
        "evidence": ["The reply uses obligation and immediate timing wording."],
        "features": features(pressure_risk=1, boundary_fit=0, communication_fit=0),
    },
    {
        "category": "low_pressure",
        "text_a": "Can you look at this today?",
        "text_b": "I can look this afternoon, and no pressure if tomorrow is easier.",
        "label": "boundary_fit",
        "label_value": 1,
        "evidence": ["The reply preserves the ask while lowering pressure."],
        "features": features(clarity_fit=1, boundary_fit=1, communication_fit=1, cognitive_load_fit=1),
    },
    {
        "category": "specificity",
        "text_a": "When should I call?",
        "text_b": "Call at 6:30pm after the meeting.",
        "label": "clarity_fit",
        "label_value": 1,
        "evidence": ["The reply gives a concrete time and context."],
        "features": features(clarity_fit=1, communication_fit=1, cognitive_load_fit=1),
    },
    {
        "category": "vague_reply",
        "text_a": "What time works for you?",
        "text_b": "Soon maybe, not sure.",
        "label": "clarity_fit",
        "label_value": 0,
        "evidence": ["The reply does not provide a concrete time."],
        "features": features(clarity_fit=0, communication_fit=0, cognitive_load_fit=1, answer_evasion_pattern=1),
    },
    {
        "category": "specificity_drop",
        "text_a": "Can you confirm Friday at 3pm at the station?",
        "text_b": "Maybe later.",
        "label": "specificity_drop",
        "label_value": 1,
        "evidence": ["The later reply has fewer concrete details than the earlier ask."],
        "features": features(communication_fit=0, specificity_drop=1, answer_evasion_pattern=1),
    },
    {
        "category": "contradiction",
        "text_a": "I can meet Friday.",
        "text_b": "I cannot meet Friday.",
        "label": "contradiction_against_prior_message",
        "label_value": 1,
        "evidence": ["The later reply conflicts with an earlier stated availability."],
        "features": features(communication_fit=0, inconsistency_cues=1, contradiction_against_prior_message=1),
    },
    {
        "category": "unsupported_claim_shift",
        "text_a": "Can we keep this focused on the plan?",
        "text_b": "You always make this difficult.",
        "label": "unsupported_claim_shift",
        "label_value": 1,
        "evidence": ["The reply introduces a broad claim without concrete supporting detail."],
        "features": features(communication_fit=0, inconsistency_cues=1, unsupported_claim_shift=1, pressure_risk=1),
    },
    {
        "category": "answer_evasion",
        "text_a": "Can you say yes or no to Friday?",
        "text_b": "Anyway, how was your day?",
        "label": "answer_evasion_pattern",
        "label_value": 1,
        "evidence": ["The reply changes topic instead of answering the direct ask."],
        "features": features(communication_fit=0, answer_evasion_pattern=1),
    },
    {
        "category": "overload",
        "text_a": "Can you review the plan, check the dates, compare the notes, send the update, and confirm the budget before Friday?",
        "text_b": "I can review the plan first, then confirm the budget tomorrow.",
        "label": "cognitive_load_fit",
        "label_value": 0,
        "evidence": ["The first message includes several asks in one message."],
        "features": features(clarity_fit=0, communication_fit=0, cognitive_load_fit=0),
    },
    {
        "category": "repair",
        "text_a": "That came out too sharp.",
        "text_b": "Sorry, let me rephrase: can we pick a time that works for both of us?",
        "label": "repair_fit",
        "label_value": 1,
        "evidence": ["The reply uses repair wording and restates a clear ask."],
        "features": features(clarity_fit=1, boundary_fit=1, repair_fit=1, communication_fit=1, cognitive_load_fit=1),
    },
    {
        "category": "consent_clarity",
        "text_a": "Would it be okay to share the plan with the group?",
        "text_b": "Yes, that is okay with me.",
        "label": "boundary_fit",
        "label_value": 1,
        "evidence": ["The reply gives explicit permission to the request."],
        "features": features(clarity_fit=1, boundary_fit=1, communication_fit=1, cognitive_load_fit=1),
    },
    {
        "category": "boundary_respect",
        "text_a": "Can I ask about your schedule?",
        "text_b": "Yes, and you can say no to sharing details if needed.",
        "label": "boundary_fit",
        "label_value": 1,
        "evidence": ["The reply includes explicit opt-out wording."],
        "features": features(boundary_fit=1, communication_fit=1, cognitive_load_fit=1),
    },
    {
        "category": "boundary_pressure",
        "text_a": "I would rather keep my location private.",
        "text_b": "You have to share your location right now.",
        "label": "pressure_risk",
        "label_value": 1,
        "evidence": ["The reply pressures for a boundary-sensitive detail."],
        "features": features(boundary_fit=0, communication_fit=0, pressure_risk=1),
    },
]


def build_row(index: int, scenario: dict[str, Any]) -> dict[str, Any]:
    suffix = index // len(SCENARIOS) + 1
    text_a = f"{scenario['text_a']} [synthetic variant {suffix}]"
    text_b = f"{scenario['text_b']} [synthetic variant {suffix}]"
    return {
        "pair_id": f"synthetic_{index + 1:03d}",
        "source_type": "synthetic_fixture",
        "categories": [scenario["category"]],
        "text_a": text_a,
        "text_b": text_b,
        "label": scenario["label"],
        "label_value": scenario["label_value"],
        "evidence": list(scenario["evidence"]),
        "features": dict(scenario["features"]),
        "blocked_interpretations": list(BLOCKED_INTERPRETATIONS),
        "provenance": {
            "created_by": "codex",
            "not_copied_from_real_chat": True,
            "synthetic": True,
            "template_category": scenario["category"],
        },
    }


def generate_rows(count: int) -> list[dict[str, Any]]:
    if count < len(SCENARIOS):
        raise ValueError(f"count must be at least {len(SCENARIOS)} to cover all required categories")
    return [build_row(index, SCENARIOS[index % len(SCENARIOS)]) for index in range(count)]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic Vibe match-pair fixtures.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--count", type=int, default=150)
    args = parser.parse_args(argv)

    rows = generate_rows(args.count)
    write_jsonl(Path(args.out), rows)
    print(json.dumps({"status": "generated", "row_count": len(rows), "out": args.out}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
