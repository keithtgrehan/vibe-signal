"""Optional Silero VAD helpers for speech-region and pause estimation."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

HAS_SILERO_VAD = True
try:  # pragma: no cover - optional dependency
    from silero_vad import get_speech_timestamps, load_silero_vad, read_audio
except Exception:  # pragma: no cover - optional dependency
    HAS_SILERO_VAD = False
    get_speech_timestamps = None
    load_silero_vad = None
    read_audio = None


@lru_cache(maxsize=1)
def _load_model():
    if not HAS_SILERO_VAD or load_silero_vad is None:
        return None
    try:
        return load_silero_vad()
    except Exception:  # pragma: no cover - environment specific
        return None


def silero_vad_available() -> bool:
    return _load_model() is not None and read_audio is not None and get_speech_timestamps is not None


def detect_speech_regions(
    audio_path: str | Path,
    *,
    sampling_rate: int = 16000,
    enabled: bool = True,
) -> list[dict[str, float]]:
    if not enabled or not silero_vad_available():
        return []
    path = Path(audio_path).expanduser().resolve()
    if not path.exists():
        return []
    try:
        waveform = read_audio(str(path), sampling_rate=sampling_rate)
        timestamps = get_speech_timestamps(waveform, _load_model(), sampling_rate=sampling_rate)
    except Exception:  # pragma: no cover - environment specific
        return []
    regions = []
    for item in timestamps or []:
        start = float(item.get("start", 0.0)) / sampling_rate
        end = float(item.get("end", 0.0)) / sampling_rate
        if end <= start:
            continue
        regions.append(
            {
                "start": round(start, 4),
                "end": round(end, 4),
                "duration_s": round(end - start, 4),
            }
        )
    return regions


def _clip_vad_segments(vad_segments: list[dict[str, Any]], start: float, end: float) -> list[tuple[float, float]]:
    clipped: list[tuple[float, float]] = []
    for row in vad_segments:
        seg_start = float(row.get("start", 0.0) or 0.0)
        seg_end = float(row.get("end", 0.0) or 0.0)
        overlap_start = max(seg_start, start)
        overlap_end = min(seg_end, end)
        if overlap_end > overlap_start:
            clipped.append((overlap_start, overlap_end))
    return sorted(clipped)


def compute_vad_pause_metrics(
    vad_segments: list[dict[str, Any]],
    *,
    start_time_s: float,
    end_time_s: float,
    min_pause_ms: float = 120.0,
    burst_pause_ms: float = 450.0,
) -> dict[str, float]:
    duration_s = max(float(end_time_s) - float(start_time_s), 0.0)
    if duration_s <= 0.0:
        return {
            "silence_ratio": 0.0,
            "pause_count": 0.0,
            "pause_density_per_10s": 0.0,
            "pause_burst_count": 0.0,
            "mean_pause_ms": 0.0,
            "max_pause_ms": 0.0,
            "speech_duration_s": 0.0,
        }
    clipped = _clip_vad_segments(vad_segments, start_time_s, end_time_s)
    if not clipped:
        return {
            "silence_ratio": 1.0,
            "pause_count": 1.0,
            "pause_density_per_10s": round(1.0 / max(duration_s / 10.0, 1e-6), 4),
            "pause_burst_count": 1.0 if duration_s * 1000.0 >= burst_pause_ms else 0.0,
            "mean_pause_ms": round(duration_s * 1000.0, 1),
            "max_pause_ms": round(duration_s * 1000.0, 1),
            "speech_duration_s": 0.0,
        }
    speech_duration_s = sum(end - start for start, end in clipped)
    pauses_ms: list[float] = []
    cursor = start_time_s
    for speech_start, speech_end in clipped:
        gap_ms = max((speech_start - cursor) * 1000.0, 0.0)
        if gap_ms >= min_pause_ms:
            pauses_ms.append(gap_ms)
        cursor = speech_end
    trailing_gap_ms = max((end_time_s - cursor) * 1000.0, 0.0)
    if trailing_gap_ms >= min_pause_ms:
        pauses_ms.append(trailing_gap_ms)
    pause_count = len(pauses_ms)
    return {
        "silence_ratio": round(max(duration_s - speech_duration_s, 0.0) / duration_s, 4),
        "pause_count": float(pause_count),
        "pause_density_per_10s": float(pause_count / max(duration_s / 10.0, 1e-6)),
        "pause_burst_count": float(sum(1 for value in pauses_ms if value >= burst_pause_ms)),
        "mean_pause_ms": round(sum(pauses_ms) / pause_count, 1) if pause_count else 0.0,
        "max_pause_ms": round(max(pauses_ms), 1) if pauses_ms else 0.0,
        "speech_duration_s": round(speech_duration_s, 4),
    }


def leading_vad_silence_before(
    vad_segments: list[dict[str, Any]],
    *,
    start_time_s: float,
    lookback_s: float = 2.0,
) -> float:
    if not vad_segments:
        return 0.0
    previous_end = max(
        (
            float(row.get("end", 0.0) or 0.0)
            for row in vad_segments
            if float(row.get("end", 0.0) or 0.0) <= float(start_time_s)
        ),
        default=float(start_time_s),
    )
    gap_s = max(float(start_time_s) - previous_end, 0.0)
    return round(min(gap_s, float(lookback_s)) * 1000.0, 1)
