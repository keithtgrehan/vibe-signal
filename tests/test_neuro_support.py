from __future__ import annotations

import json

from vibesignal_ai.features.neuro_support import (
    detect_message_overload,
    detect_pressure_language,
    detect_unclear_ask,
    suggest_literal_summary,
    suggest_lower_pressure_rewrite,
    suggest_more_direct_rewrite,
    suggest_repair_message,
)
from vibesignal_ai.safety.validator import validate_payload


BLOCKED_PHRASES = (
    "they love you",
    "they are lying",
    "they are manipulating you",
    "they are autistic",
    "they have ADHD",
    "make them",
    "trigger their attachment",
    "use their vulnerability",
)


def assert_safe_card(card: dict) -> None:
    assert set(card) == {"card_type", "status", "summary", "observations", "suggestion", "limits"}
    assert card["status"] in {"ok", "empty", "blocked"}
    assert isinstance(card["observations"], list)
    assert isinstance(card["limits"], list)
    assert validate_payload(card) == []
    text = json.dumps(card).lower()
    for phrase in BLOCKED_PHRASES:
        assert phrase.lower() not in text


def test_detect_message_overload_returns_safe_shortening_card() -> None:
    card = detect_message_overload(
        "I wanted to ask about Friday and also Saturday and the plan for the train, "
        "the booking, dinner, and whether you can confirm everything before tonight "
        "because I am trying to coordinate several things at once."
    )

    assert_safe_card(card)
    assert card["summary"] == "This may be easier to read if shortened."


def test_detect_unclear_ask_and_more_direct_rewrite_are_safe() -> None:
    unclear = detect_unclear_ask("Maybe later would be fine, just wondering about the plan.")
    rewrite = suggest_more_direct_rewrite("Maybe later would be fine, just wondering about the plan.")

    assert_safe_card(unclear)
    assert_safe_card(rewrite)
    assert unclear["summary"] == "The ask is not explicit."
    assert rewrite["suggestion"].startswith("A more direct version could be...")


def test_pressure_language_and_lower_pressure_rewrite_are_safe() -> None:
    pressure = detect_pressure_language("You must reply now or else this will be a problem.")
    rewrite = suggest_lower_pressure_rewrite("You must reply now or else this will be a problem.")

    assert_safe_card(pressure)
    assert_safe_card(rewrite)
    assert pressure["status"] == "ok"
    assert rewrite["suggestion"].startswith("A lower-pressure version could be...")


def test_literal_summary_and_repair_message_do_not_guess_feelings() -> None:
    summary = suggest_literal_summary("I can meet Friday. Please confirm the time.")
    repair = suggest_repair_message("I asked too many things at once.")

    assert_safe_card(summary)
    assert_safe_card(repair)
    assert "without guessing how the other person feels" in summary["limits"]
    assert repair["card_type"] == "repair_message"


def test_empty_input_returns_empty_status() -> None:
    assert detect_message_overload(" ")["status"] == "empty"
    assert detect_unclear_ask("")["status"] == "empty"
