from __future__ import annotations

from pathlib import Path


def test_cue_preconditions_v2_documents_context_requirements() -> None:
    text = Path("docs/research/cue_preconditions_v2.md").read_text(encoding="utf-8").lower()

    assert "single-message allowed" in text
    assert "multi-message required" in text
    assert "specificity_drop" in text
    assert "contradiction_against_prior_message" in text
    assert "answer_evasion_pattern" in text
    assert "urgency alone is not pressure" in text
    assert "ambiguity is not hidden intent" in text
    assert "contradiction is not lying" in text
