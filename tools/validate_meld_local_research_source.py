#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.transcript_nlp_local_research_common import MELD_EMOTIONS, MELD_SENTIMENTS, utc_now, write_json  # noqa: E402


DATASET_ID = "declare-lab/MELD"
HF_API_URL = f"https://huggingface.co/api/datasets/{DATASET_ID}"
LICENSE_ID = "gpl-3.0"
REQUIRED_FILES = {
    "train": "train_sent_emo.csv",
    "validation": "dev_sent_emo.csv",
    "test": "test_sent_emo.csv",
}
MEDIA_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".webm", ".avi", ".mkv"}
REQUIRED_COLUMNS = {
    "Utterance",
    "Emotion",
    "Sentiment",
    "Dialogue_ID",
    "Utterance_ID",
}


def _read_json_url(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{url} did not return a JSON object")
    return payload


def _license_values(payload: dict[str, Any]) -> list[str]:
    card = payload.get("cardData") if isinstance(payload.get("cardData"), dict) else {}
    value = card.get("license")
    values: list[str] = []
    if isinstance(value, list):
        values.extend(str(item).strip().lower() for item in value)
    elif value:
        values.append(str(value).strip().lower())
    values.extend(str(tag).split("license:", 1)[1].lower() for tag in payload.get("tags", []) if str(tag).startswith("license:"))
    return sorted(set(values))


def validate_meld_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    licenses = _license_values(payload)
    if LICENSE_ID not in licenses:
        raise ValueError(f"MELD metadata must include {LICENSE_ID}; found {licenses}")
    return {"license": LICENSE_ID, "dataset_id": payload.get("id", DATASET_ID)}


def _reject_media_files(input_dir: Path) -> None:
    media = sorted(path for path in input_dir.rglob("*") if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS)
    if media:
        examples = ", ".join(str(path.relative_to(input_dir)) for path in media[:5])
        raise ValueError(f"MELD local research source must be text CSV only; media files found: {examples}")


def _validate_csv(path: Path) -> tuple[int, dict[str, int], dict[str, int]]:
    if not path.exists():
        raise FileNotFoundError(f"missing MELD CSV: {path}")
    row_count = 0
    emotion_counts: dict[str, int] = {}
    sentiment_counts: dict[str, int] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"{path.name} missing required columns: {sorted(missing_columns)}")
        for index, row in enumerate(reader, start=2):
            utterance = str(row.get("Utterance", "")).strip()
            emotion = str(row.get("Emotion", "")).strip().lower()
            sentiment = str(row.get("Sentiment", "")).strip().lower()
            if not utterance:
                raise ValueError(f"{path.name}:{index}: Utterance cannot be empty")
            if emotion not in MELD_EMOTIONS:
                raise ValueError(f"{path.name}:{index}: unsupported Emotion {emotion!r}")
            if sentiment not in MELD_SENTIMENTS:
                raise ValueError(f"{path.name}:{index}: unsupported Sentiment {sentiment!r}")
            row_count += 1
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
    return row_count, emotion_counts, sentiment_counts


def build_manifest(input_dir: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    _reject_media_files(input_dir)
    split_counts: dict[str, int] = {}
    emotion_counts: dict[str, int] = {}
    sentiment_counts: dict[str, int] = {}
    files: dict[str, str] = {}
    for split, filename in REQUIRED_FILES.items():
        count, split_emotions, split_sentiments = _validate_csv(input_dir / filename)
        split_counts[split] = count
        files[split] = str((input_dir / filename).resolve())
        for label, value in split_emotions.items():
            emotion_counts[label] = emotion_counts.get(label, 0) + value
        for label, value in split_sentiments.items():
            sentiment_counts[label] = sentiment_counts.get(label, 0) + value
    return {
        "source_id": "meld",
        "source_tier": "meld_local_research_gpl3_nc",
        "dataset_id": DATASET_ID,
        "dataset_url": "https://huggingface.co/datasets/declare-lab/MELD",
        "project_url": "https://github.com/declare-lab/MELD",
        "dataset_site_url": "https://affective-meld.github.io/",
        "license_id": LICENSE_ID,
        "license_metadata_confirmed": True,
        "local_only": True,
        "text_only": True,
        "audio_video_used": False,
        "commercial_training_allowed": False,
        "research_training_allowed": True,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "row_commit_allowed": False,
        "raw_rows_committed": False,
        "aggregate_report_only": True,
        "files": files,
        "splits": split_counts,
        "emotion_counts": dict(sorted(emotion_counts.items())),
        "sentiment_counts": dict(sorted(sentiment_counts.items())),
        "content_warning": "MELD contains TV-show transcript utterances with emotion and sentiment labels. Labels are weak signals, not emotion truth.",
        "metadata_snapshot": metadata,
        "created_at": utc_now(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a local-only text CSV MELD research source and write a fail-closed manifest.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--manifest-out", required=True)
    parser.add_argument("--metadata-json", help="Optional local metadata JSON for tests/offline verification.")
    args = parser.parse_args(argv)

    try:
        if args.metadata_json:
            metadata_payload = json.loads(Path(args.metadata_json).read_text(encoding="utf-8"))
        else:
            metadata_payload = _read_json_url(HF_API_URL)
        metadata = validate_meld_metadata(metadata_payload)
        manifest = build_manifest(Path(args.input_dir), metadata)
        write_json(Path(args.manifest_out), manifest)
    except Exception as exc:
        print(f"MELD local research source validation failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "validated_meld_local_research_source",
                "input_dir": str(Path(args.input_dir)),
                "manifest_out": str(Path(args.manifest_out)),
                "splits": manifest["splits"],
                "audio_video_used": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
