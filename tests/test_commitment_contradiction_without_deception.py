from __future__ import annotations

import re

from vibesignal_ai.matching.features import extract_matching_features


FORBIDDEN_DECEPTION_PATTERNS = (
    r"\blying\b",
    r"\blie\b",
    r"\blies\b",
    r"\bdeception\b",
    r"\bdeceptive\b",
    r"\bcheating\b",
)


def test_commitment_contradiction_is_observable_not_deception_claim() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "other", "text": "I can meet Friday at 7pm."},
            {"id": "m2", "author": "other", "text": "I can't meet Friday at 7pm."},
        ],
        conversation_id="synthetic_commitment_contradiction",
    )

    assert result.contradiction_against_prior_message
    rendered = " ".join(
        f"{row.get('safe_phrase', '')} {row.get('explanation', '')}"
        for row in result.contradiction_against_prior_message
    ).lower()
    assert not any(re.search(pattern, rendered) for pattern in FORBIDDEN_DECEPTION_PATTERNS)


def test_ambiguity_is_not_hidden_intent_or_attraction() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "self", "text": "Can we talk tonight?"},
            {"id": "m2", "author": "other", "text": "Maybe later."},
        ],
        conversation_id="synthetic_ambiguity_not_hidden_intent",
    )

    rendered = " ".join(
        f"{row.get('safe_phrase', '')} {row.get('explanation', '')}"
        for row in result.all_evidence
    ).lower()
    assert "hidden intent" not in rendered
    assert "attraction" not in rendered
