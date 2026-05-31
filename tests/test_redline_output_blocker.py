from __future__ import annotations

from vibesignal_ai.safety.redline_output_blocker import check_output_text, validate_output_text


def test_blocked_output_returns_category_and_replacement_without_echoing_raw_text() -> None:
    raw = "They are lying."

    result = check_output_text(raw)

    assert result["status"] == "block"
    assert "deception_or_truth" in result["categories"]
    assert result["safe_replacement"]
    assert raw not in result["safe_replacement"]


def test_allowed_neutral_pattern_output_passes() -> None:
    text = "Later replies contain more hedging markers than earlier replies."

    assert check_output_text(text)["status"] == "allow"
    assert validate_output_text(text) == []
