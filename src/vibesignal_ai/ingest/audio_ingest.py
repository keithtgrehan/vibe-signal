"""Audio ingest helpers and transcript-segment normalization."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

from ..audio.opensmile_adapter import extract_opensmile_features
from ..audio.segment_aggregate import aggregate_audio_segments
from ..audio.transcriber import transcribe_audio
from ..audio.vad import detect_speech_regions
from ..config import runtime_flags
from ..utils.io_utils import write_json
from .normalization import enrich_messages


def normalize_audio(input_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(output_path),
    ]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Audio normalization failed for {input_path}: {(proc.stderr or proc.stdout).strip()}"
        )
    return output_path


def _segments_to_messages(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for index, segment in enumerate(segments, start=1):
        messages.append(
            {
                "message_id": index,
                "speaker": str(segment.get("speaker", "speaker_1")),
                "timestamp": None,
                "text": str(segment.get("text", "")).strip(),
                "is_system": False,
                "start": float(segment.get("start", 0.0) or 0.0),
                "end": float(segment.get("end", 0.0) or 0.0),
                "source": "audio_transcript",
            }
        )
    return enrich_messages(messages)


def _load_segments_file(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise RuntimeError("Transcript segment JSON must be a list of objects.")
    segments: list[dict[str, Any]] = []
    for index, row in enumerate(payload, start=1):
        if not isinstance(row, dict):
            continue
        segments.append(
            {
                "segment_id": index,
                "speaker": str(row.get("speaker", "speaker_1")),
                "start": float(row.get("start", 0.0) or 0.0),
                "end": float(row.get("end", row.get("start", 0.0)) or 0.0),
                "text": str(row.get("text", "")).strip(),
                "detected_language": row.get("detected_language"),
            }
        )
    return segments


def ingest_audio(
    input_path: str | Path,
    *,
    raw_dir: str | Path,
    processed_dir: str | Path,
) -> dict[str, Any]:
    source = Path(input_path).expanduser().resolve()
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    copied_input = raw_dir / source.name
    if source.exists():
        shutil.copy2(source, copied_input)

    if source.suffix.lower() == ".json":
        segments = _load_segments_file(source)
        vad_segments: list[dict[str, Any]] = []
        opensmile_features = {
            "enabled": bool(runtime_flags.ENABLE_OPENSMILE),
            "available": False,
            "backend": "not_applicable",
            "summary": {},
            "segment_features": [],
        }
    else:
        normalized_path = processed_dir / "normalized.wav"
        normalize_audio(source, normalized_path)
        vad_segments = detect_speech_regions(
            normalized_path,
            enabled=bool(runtime_flags.ENABLE_VAD),
        )
        raw_segments = transcribe_audio(str(normalized_path), verbose=False)
        segments = [
            {
                "segment_id": index,
                "speaker": "speaker_1",
                "start": float(item.get("start", 0.0) or 0.0),
                "end": float(item.get("end", 0.0) or 0.0),
                "text": str(item.get("text", "")).strip(),
            }
            for index, item in enumerate(raw_segments, start=1)
        ]
        opensmile_features = extract_opensmile_features(
            normalized_path,
            segments=segments,
            enabled=bool(runtime_flags.ENABLE_OPENSMILE),
        )

    messages = _segments_to_messages(segments)
    segment_metrics = aggregate_audio_segments(
        segments,
        vad_segments=vad_segments or None,
        opensmile_payload=opensmile_features if opensmile_features.get("available") else None,
    )

    write_json(processed_dir / "segments.json", segments)
    write_json(processed_dir / "segment_metrics.json", segment_metrics)
    if vad_segments:
        write_json(processed_dir / "vad_segments.json", vad_segments)
    if opensmile_features.get("enabled"):
        write_json(processed_dir / "opensmile_features.json", opensmile_features)
    write_json(raw_dir / "messages.json", messages)

    return {
        "messages": messages,
        "segments": segments,
        "segment_metrics": segment_metrics,
        "vad_segments": vad_segments,
        "opensmile_features": opensmile_features,
    }
