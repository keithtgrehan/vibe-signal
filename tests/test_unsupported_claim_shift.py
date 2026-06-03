from __future__ import annotations

import re

from vibesignal_ai.matching.features import extract_matching_features


def test_claim_shift_has_evidence_without_deception_claim() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "other", "text": "The plan is approved."},
            {"id": "m2", "author": "other", "text": "The plan is not approved after all."},
        ],
        conversation_id="synthetic_unsupported_claim_shift",
    )

    assert result.unsupported_claim_shift
    rendered = " ".join(
        f"{row.get('safe_phrase', '')} {row.get('explanation', '')}"
        for row in result.unsupported_claim_shift
    ).lower()
    assert not re.search(r"\b(?:lying|deception|cheating|hidden intent)\b", rendered)

