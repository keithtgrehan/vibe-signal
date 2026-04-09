from __future__ import annotations

from pathlib import Path

from vibesignal_ai.audio.segment_aggregate import aggregate_audio_segments
from vibesignal_ai.audio import vad


def test_silero_vad_adapter_falls_back_gracefully(monkeypatch, tmp_path: Path) -> None:
    missing = tmp_path / "missing.wav"

    monkeypatch.setattr(vad, "HAS_SILERO_VAD", False)
    vad._load_model.cache_clear()

    assert vad.silero_vad_available() is False
    assert vad.detect_speech_regions(missing) == []


def test_segment_aggregate_uses_vad_metrics_when_available() -> None:
    rows = aggregate_audio_segments(
        [
            {
                "segment_id": 1,
                "speaker": "candidate",
                "start": 1.0,
                "end": 4.0,
                "text": "I can walk through the rollout in two phases.",
            }
        ],
        vad_segments=[
            {"start": 0.0, "end": 0.6},
            {"start": 1.4, "end": 2.3},
            {"start": 2.9, "end": 3.8},
        ],
    )

    assert rows[0]["pause_source"] == "silero_vad"
    assert rows[0]["pause_before_answer_ms"] == 400.0
    assert rows[0]["pause_count"] >= 1
