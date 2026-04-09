from __future__ import annotations

from vibesignal_ai.safety.validator import validate_text


def test_safety_validator_rejects_banned_terms() -> None:
    errors = validate_text("This clearly means they are lying.", field_name="headline")
    assert errors
    assert "headline contains banned output language" in errors[0]


def test_safety_validator_rejects_soft_verdict_language() -> None:
    errors = validate_text(
        "This suggests the candidate will not get the job.",
        field_name="headline",
    )
    assert errors
    assert any("implication-heavy verdict phrasing" in error for error in errors)
