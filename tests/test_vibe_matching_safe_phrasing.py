from __future__ import annotations

import re

from vibesignal_ai.matching import match_conversation
from vibesignal_ai.safety.redline_output_blocker import check_output_text
from vibesignal_ai.safety.validator import validate_payload


FORBIDDEN_PATTERNS = (
    r"\blied?\b",
    r"\bcheat",
    r"\battract",
    r"\bdiagnos",
    r"\badhd\b",
    r"\bautis",
    r"\battachment\b",
    r"\bsecret",
    r"\bhidden intent\b",
    r"\bmanipulat",
)


def test_matching_output_uses_observable_pattern_language_only() -> None:
    result = match_conversation(
        {
            "conversation_id": "synthetic_safe_match_language",
            "messages": [
                {"id": "m1", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T10:00:00Z"},
                {"id": "m2", "author": "other", "text": "Maybe later. Anyway, you never listen.", "created_at": "2026-05-31T10:01:00Z"},
            ],
            "user_preferences": {"prefers_directness": True, "prefers_low_pressure": True, "prefers_explicit_plans": True},
        }
    )

    user_facing_text = " ".join(
        [
            result["safe_summary"],
            result["safe_explanation"],
            " ".join(result["top_alignment_factors"]),
            " ".join(result["top_friction_factors"]),
            " ".join(item.get("safe_phrase", "") for item in result["evidence"]),
        ]
    )
    for pattern in FORBIDDEN_PATTERNS:
        assert not re.search(pattern, user_facing_text, flags=re.IGNORECASE), pattern
    assert validate_payload(user_facing_text) == []
    assert check_output_text(result["safe_summary"])["status"] == "allow"
    assert "observable communication-pattern compatibility" in result["safe_summary"]


def test_matcher_replaces_redline_summary_if_unsafe_text_is_provided() -> None:
    result = match_conversation(
        {
            "conversation_id": "synthetic_safe_replacement",
            "messages": [
                {"id": "m1", "author": "self", "text": "Can you confirm Friday?"},
                {"id": "m2", "author": "other", "text": "Maybe later."},
            ],
            "debug_summary_override": "They are lying.",
        }
    )

    assert result["redline_status"] == "block"
    assert result["safe_summary"] == "This match result describes observable communication patterns only."
    assert check_output_text(result["safe_summary"])["status"] == "allow"
