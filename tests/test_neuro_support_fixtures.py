from __future__ import annotations

import json
from pathlib import Path

from vibesignal_ai.features.neuro_support import (
    detect_message_overload,
    detect_pressure_language,
    suggest_literal_summary,
    suggest_more_direct_rewrite,
    suggest_repair_message,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "neuro_support" / "neuro_support_cases.json"

REQUIRED_KEYS = {
    "fixture_id",
    "category",
    "user_context",
    "incoming_message",
    "user_request",
    "expected_behavior",
    "must_not",
    "expected_safe_card_type",
}
EXPECTED_CATEGORIES = {
    "ambiguous_message",
    "silence_no_reply",
    "emoji_only",
    "indirect_interest",
    "indirect_rejection",
    "literal_interpretation",
    "directness_preference",
    "over_explaining",
    "emotional_surge",
    "repair_after_overload",
    "missed_plan_repair",
    "texting_boundary",
    "late_night_boundary",
    "unwanted_sexual_content",
    "consent_escalation",
    "meeting_pressure",
    "privacy_pressure",
    "disclosure_decision",
    "masking_request",
    "partner_preference",
    "ending_contact",
    "manipulation_request",
    "attachment_scoring_request",
    "safety_escalation",
    "data_privacy",
    "low_cognitive_load_summary",
    "tone_preview",
    "autonomy_user_sends_anyway",
    "cross_cultural_ambiguity",
    "multi_turn_repair_space_request",
}
SAFETY_TERMS = {
    "infer",
    "diagnos",
    "pressure",
    "coerc",
    "mind-read",
    "surveillance",
    "consent",
    "intent",
    "guilt",
    "control",
    "threat",
    "privacy",
    "blame",
    "label",
    "stereotype",
    "monitor",
}


def load_cases() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_neuro_support_fixture_schema_and_categories() -> None:
    rows = load_cases()

    assert rows
    assert {row["category"] for row in rows} >= EXPECTED_CATEGORIES
    assert len({row["fixture_id"] for row in rows}) == len(rows)
    for row in rows:
        assert REQUIRED_KEYS <= set(row)
        assert row["fixture_id"].startswith("synthetic_neuro_")
        assert row["user_context"] == "Synthetic scenario only."
        assert isinstance(row["expected_behavior"], list) and row["expected_behavior"]
        assert isinstance(row["must_not"], list) and row["must_not"]
        assert any(term in " ".join(row["must_not"]).lower() for term in SAFETY_TERMS)
        assert row["expected_safe_card_type"]


def test_neuro_support_fixtures_are_compatible_with_existing_cards() -> None:
    rows = load_cases()
    by_type = {row["expected_safe_card_type"]: row for row in rows}

    assert detect_message_overload(by_type["message_overload"]["incoming_message"])["card_type"] == "message_overload"
    assert detect_pressure_language(by_type["pressure_language"]["incoming_message"])["card_type"] == "pressure_language"
    assert suggest_more_direct_rewrite(by_type["more_direct_rewrite"]["incoming_message"])["card_type"] == "more_direct_rewrite"
    assert suggest_literal_summary(by_type["literal_summary"]["incoming_message"])["card_type"] == "literal_summary"
    assert suggest_repair_message(by_type["repair_message"]["incoming_message"])["card_type"] == "repair_message"
