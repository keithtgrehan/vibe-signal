from __future__ import annotations

from pathlib import Path

from vibesignal_ai.audio.opensmile_adapter import extract_opensmile_features
from vibesignal_ai.config import runtime_flags
from vibesignal_ai.features.consistency import analyze_consistency
from vibesignal_ai.ingest.audio_ingest import ingest_audio
from vibesignal_ai.ingest.segmentation import group_turns, link_response_pairs
from vibesignal_ai.nlp.contradiction_adapter import score_statement_relation


MESSAGES = [
    {"message_id": 1, "speaker": "Alex", "speaker_key": "alex", "text": "Are you still coming tonight?", "analysis_text": "Are you still coming tonight?", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T09:00:00"},
    {"message_id": 2, "speaker": "Sam", "speaker_key": "sam", "text": "Yes, I can be there by 7 because I leave work at 6.", "analysis_text": "Yes, I can be there by 7 because I leave work at 6.", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T09:01:00"},
    {"message_id": 3, "speaker": "Alex", "speaker_key": "alex", "text": "Can you confirm once you leave?", "analysis_text": "Can you confirm once you leave?", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T09:03:00"},
    {"message_id": 4, "speaker": "Sam", "speaker_key": "sam", "text": "Maybe later... not sure yet.", "analysis_text": "Maybe later... not sure yet.", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T09:25:00"},
]


def test_runtime_flag_defaults_stay_off() -> None:
    snapshot = runtime_flags.runtime_flag_snapshot()
    assert snapshot["enable_opensmile"] is False
    assert snapshot["enable_nli"] is False
    assert snapshot["enable_vad"] is False


def test_opensmile_adapter_falls_back_cleanly(tmp_path: Path) -> None:
    missing = tmp_path / "missing.wav"
    payload = extract_opensmile_features(missing, enabled=True)
    assert payload["enabled"] is True
    assert payload["available"] is False
    assert payload["summary"] == {}


def test_nli_adapter_falls_back_cleanly() -> None:
    payload = score_statement_relation(
        "I will arrive at 7.",
        "I can be there by 7.",
        enabled=True,
        model_name="local-missing-model",
    )
    assert payload["available"] is False
    assert payload["relation"] == "unavailable"


def test_consistency_stays_deterministic_when_optional_nli_disabled(monkeypatch) -> None:
    monkeypatch.setattr(runtime_flags, "ENABLE_NLI", False)
    turns = group_turns(MESSAGES)
    pairs = link_response_pairs(turns)
    consistency = analyze_consistency(MESSAGES, turns=turns, response_pairs=pairs)

    assert consistency["metrics"]["optional_nli"]["enabled"] is False
    assert consistency["metrics"]["optional_nli"]["available_pair_count"] == 0


def test_audio_ingest_stays_clean_when_optional_audio_features_disabled(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fixture = Path(__file__).parent / "fixtures" / "interview_segments.json"

    monkeypatch.setattr(runtime_flags, "ENABLE_OPENSMILE", False)
    monkeypatch.setattr(runtime_flags, "ENABLE_VAD", False)

    payload = ingest_audio(
        fixture,
        raw_dir=tmp_path / "raw",
        processed_dir=tmp_path / "processed",
    )

    assert payload["opensmile_features"]["available"] is False
    assert all(
        row["acoustic_support_source"] == "none"
        for row in payload["segment_metrics"]
    )
