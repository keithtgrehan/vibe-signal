from __future__ import annotations

import re
from pathlib import Path

import yaml

from vibesignal_ai.evidence.objects import validate_evidence_object
from vibesignal_ai.features.cue_taxonomy import CUE_IDS, detect_cues


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "vibe_cue_taxonomy.yml"
REQUIRED_FAMILIES = {
    "directness",
    "specificity",
    "hedging",
    "urgency",
    "reassurance",
    "pressure",
    "conflict",
    "alignment",
    "response_timing",
    "topic_shift",
    "ambiguity",
    "cognitive_load",
    "unclear_ask",
    "overloaded_message",
    "escalation_risk",
    "repair_opportunity",
    "boundary_pressure",
    "consent_clarity",
}
REQUIRED_EVIDENCE_FIELDS = {
    "cue_id",
    "cue_family",
    "evidence_text",
    "span_start",
    "span_end",
    "confidence",
    "explanation",
    "safe_phrase",
}


def load_config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def synthetic_messages() -> list[dict]:
    return [
        {"id": "m1", "author": "self", "created_at": "2026-05-31T10:00:00Z", "text": "Please confirm Friday at 3pm."},
        {"id": "m2", "author": "other", "created_at": "2026-05-31T10:01:00Z", "text": "Maybe sometime later, not sure."},
        {"id": "m3", "author": "self", "created_at": "2026-05-31T10:02:00Z", "text": "This is urgent right now."},
        {"id": "m4", "author": "other", "created_at": "2026-05-31T10:03:00Z", "text": "No pressure, when you can, all good."},
        {"id": "m5", "author": "self", "created_at": "2026-05-31T10:04:00Z", "text": "You have to send me your location right now or else."},
        {"id": "m6", "author": "other", "created_at": "2026-05-31T10:05:00Z", "text": "I'm frustrated that this became an argument."},
        {"id": "m7", "author": "self", "created_at": "2026-05-31T10:06:00Z", "text": "I agree, sounds good, we are on the same page."},
        {"id": "m8", "author": "other", "created_at": "2026-05-31T10:07:00Z", "text": "Anyway, separately, another thing for tomorrow."},
        {
            "id": "m9",
            "author": "self",
            "created_at": "2026-05-31T10:08:00Z",
            "text": (
                "Can you review the plan, confirm the budget, send the update, and check the calendar? "
                "Also, please compare the notes, rewrite the intro, and tell me what changed before Friday."
            ),
        },
        {"id": "m10", "author": "other", "created_at": "2026-05-31T10:09:00Z", "text": "Sorry, let me rephrase what I meant."},
        {"id": "m11", "author": "self", "created_at": "2026-05-31T10:10:00Z", "text": "You can say no; is that okay?"},
        {"id": "m12", "author": "self", "created_at": "2026-05-31T10:10:40Z", "text": "Just checking again."},
        {"id": "m13", "author": "self", "created_at": "2026-05-31T10:15:00Z", "text": "Can you confirm the plan?"},
        {"id": "m14", "author": "other", "created_at": "2026-05-31T10:20:00Z", "text": "Anyway, separately, another thing for tomorrow."},
        {"id": "m15", "author": "self", "created_at": "2026-05-31T10:25:00Z", "text": "Can you maybe?"},
    ]


def test_cue_taxonomy_config_covers_required_families_and_regexes_compile() -> None:
    payload = load_config()
    rows = payload["cues"]

    assert REQUIRED_FAMILIES == {row["cue_family"] for row in rows}
    assert REQUIRED_FAMILIES == CUE_IDS
    for row in rows:
        assert row["cue_id"] == row["cue_family"]
        assert row["safe_phrase"].startswith(("message contains", "text cues suggest"))
        assert row["blocked_interpretations"]
        for pattern in row.get("patterns", []):
            re.compile(pattern)


def test_detect_cues_returns_required_evidence_fields_for_all_families() -> None:
    cues = detect_cues(synthetic_messages(), conversation_id="synthetic_taxonomy_all")
    families = {cue["cue_family"] for cue in cues}

    assert REQUIRED_FAMILIES <= families
    for cue in cues:
        assert REQUIRED_EVIDENCE_FIELDS <= set(cue)
        assert cue["cue_id"] == cue["cue_family"]
        assert cue["cue_family"] in REQUIRED_FAMILIES
        assert cue["span_start"] == cue["start_offset"]
        assert cue["span_end"] == cue["end_offset"]
        assert 0 <= cue["span_start"] <= cue["span_end"]
        assert 0.0 <= cue["confidence"] <= 1.0
        assert cue["safe_phrase"].startswith(("message contains", "text cues suggest"))
        assert validate_evidence_object(cue) == []


def test_reducers_keep_reassurance_from_becoming_pressure_or_urgency() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "self", "created_at": "2026-05-31T10:00:00Z", "text": "No pressure and no rush, reply when you can."}],
        conversation_id="synthetic_reducer",
    )
    families = {cue["cue_family"] for cue in cues}

    assert "reassurance" in families
    assert "pressure" not in families
    assert "urgency" not in families
