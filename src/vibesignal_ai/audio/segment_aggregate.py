"""Lightweight audio/text segment aggregation helpers."""

from __future__ import annotations

from typing import Any

from .pause_features import (
    AudioEnvelope,
    articulation_rate_wpm,
    count_fillers,
    leading_silence_before,
    pause_stats,
    segment_rms_stats,
    silence_ratio,
    speech_rate_wpm,
)
from .vad import compute_vad_pause_metrics, leading_vad_silence_before


def _hesitation_label(score: int) -> str:
    if score >= 5:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def aggregate_audio_segments(
    segments: list[dict[str, Any]],
    *,
    envelope: AudioEnvelope | None = None,
    vad_segments: list[dict[str, Any]] | None = None,
    opensmile_payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    opensmile_segments = {
        int(item.get("segment_id", 0)): item
        for item in (opensmile_payload or {}).get("segment_features", [])
        if item.get("segment_id") is not None
    }
    opensmile_summary = (opensmile_payload or {}).get("summary", {})

    for index, segment in enumerate(segments, start=1):
        text = str(segment.get("text", "")).strip()
        segment_id = int(segment.get("segment_id", index))
        start_time_s = float(segment.get("start", 0.0) or 0.0)
        end_time_s = float(segment.get("end", start_time_s) or start_time_s)
        duration_s = max(0.0, end_time_s - start_time_s)

        filler_count, filler_matches = count_fillers(text)
        speech_rate, word_count = speech_rate_wpm(text, duration_s)

        metrics = {
            "segment_id": segment_id,
            "speaker": str(segment.get("speaker", "speaker_1")),
            "text": text,
            "start_time_s": round(start_time_s, 4),
            "end_time_s": round(end_time_s, 4),
            "segment_duration_s": round(duration_s, 4),
            "word_count": int(word_count),
            "filler_count": int(filler_count),
            "matched_fillers": filler_matches,
            "filler_density": round((filler_count / word_count) * 100.0, 4)
            if word_count
            else 0.0,
            "speech_rate_wpm": round(float(speech_rate), 2),
            "articulation_rate_wpm": round(float(articulation_rate_wpm(text, duration_s)), 2)
            if duration_s > 0.0
            else 0.0,
            "pause_before_answer_ms": None,
            "silence_ratio": 0.0,
            "pause_count": 0,
            "pause_density_per_10s": 0.0,
            "pause_burst_count": 0,
            "mean_pause_ms": 0.0,
            "max_pause_ms": 0.0,
            "mean_rms_db": 0.0,
            "rms_std_db": 0.0,
            "rms_range_db": 0.0,
            "frame_count": 0,
            "pause_source": "none",
            "acoustic_support_source": "none",
            "acoustic_energy_intensity_proxy": 0.0,
            "acoustic_voicing_ratio_proxy": 0.0,
            "acoustic_pitch_variation_proxy": 0.0,
            "acoustic_spectral_flux_proxy": 0.0,
            "acoustic_hesitation_support_proxy": 0.0,
        }

        if envelope is not None:
            silence_value, frame_count = silence_ratio(envelope, start_time_s, end_time_s)
            pauses = pause_stats(envelope, start_time_s, end_time_s)
            rms = segment_rms_stats(envelope, start_time_s, end_time_s)
            metrics.update(
                {
                    "pause_before_answer_ms": round(
                        float(leading_silence_before(envelope, start_time_s)), 1
                    ),
                    "silence_ratio": round(float(silence_value), 4),
                    "pause_count": int(pauses["pause_count"]),
                    "pause_density_per_10s": round(
                        float(pauses["pause_density_per_10s"]), 4
                    ),
                    "pause_burst_count": int(pauses["pause_burst_count"]),
                    "mean_pause_ms": round(float(pauses["mean_pause_ms"]), 1),
                    "max_pause_ms": round(float(pauses["max_pause_ms"]), 1),
                    "mean_rms_db": round(float(rms["mean_rms_db"]), 4),
                    "rms_std_db": round(float(rms["rms_std_db"]), 4),
                    "rms_range_db": round(float(rms["rms_range_db"]), 4),
                    "frame_count": int(frame_count),
                    "pause_source": "audio_envelope",
                }
            )
        elif vad_segments:
            pauses = compute_vad_pause_metrics(
                vad_segments,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
            )
            metrics.update(
                {
                    "pause_before_answer_ms": round(
                        float(
                            leading_vad_silence_before(
                                vad_segments,
                                start_time_s=start_time_s,
                            )
                        ),
                        1,
                    ),
                    "silence_ratio": round(float(pauses["silence_ratio"]), 4),
                    "pause_count": int(pauses["pause_count"]),
                    "pause_density_per_10s": round(float(pauses["pause_density_per_10s"]), 4),
                    "pause_burst_count": int(pauses["pause_burst_count"]),
                    "mean_pause_ms": round(float(pauses["mean_pause_ms"]), 1),
                    "max_pause_ms": round(float(pauses["max_pause_ms"]), 1),
                    "pause_source": "silero_vad",
                }
            )

        opensmile_metrics = opensmile_segments.get(segment_id) or opensmile_summary
        if opensmile_payload and opensmile_payload.get("available") and opensmile_metrics:
            metrics.update(
                {
                    "acoustic_support_source": "opensmile_segment"
                    if segment_id in opensmile_segments
                    else "opensmile_summary",
                    "acoustic_energy_intensity_proxy": round(
                        float(opensmile_metrics.get("energy_intensity_proxy", 0.0) or 0.0),
                        4,
                    ),
                    "acoustic_voicing_ratio_proxy": round(
                        float(opensmile_metrics.get("voicing_ratio_proxy", 0.0) or 0.0),
                        4,
                    ),
                    "acoustic_pitch_variation_proxy": round(
                        float(opensmile_metrics.get("pitch_variation_proxy", 0.0) or 0.0),
                        4,
                    ),
                    "acoustic_spectral_flux_proxy": round(
                        float(opensmile_metrics.get("spectral_flux_proxy", 0.0) or 0.0),
                        4,
                    ),
                    "acoustic_hesitation_support_proxy": round(
                        float(opensmile_metrics.get("hesitation_support_proxy", 0.0) or 0.0),
                        4,
                    ),
                }
            )

        hesitation_score = 0
        if metrics["pause_before_answer_ms"] and metrics["pause_before_answer_ms"] >= 450.0:
            hesitation_score += 2
        if metrics["filler_density"] >= 2.5:
            hesitation_score += 2
        elif metrics["filler_density"] > 0.0:
            hesitation_score += 1
        if metrics["silence_ratio"] >= 0.15:
            hesitation_score += 1
        if metrics["speech_rate_wpm"] and metrics["speech_rate_wpm"] < 90.0:
            hesitation_score += 1

        metrics["hesitation_score"] = hesitation_score
        metrics["hesitation_label"] = _hesitation_label(hesitation_score)
        rows.append(metrics)

    return rows
