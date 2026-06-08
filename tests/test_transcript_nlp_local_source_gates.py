from __future__ import annotations

import csv
import json
from pathlib import Path

from tools.prepare_goemotions_local_research_cache import validate_goemotions_metadata
from tools.validate_meld_local_research_source import build_manifest as build_meld_manifest
from tools.validate_meld_local_research_source import validate_meld_metadata


def _goemotions_metadata(license_value: str = "apache-2.0") -> dict[str, object]:
    return {
        "id": "google-research-datasets/go_emotions",
        "tags": [f"license:{license_value}"],
        "cardData": {
            "license": [license_value],
            "dataset_info": [
                {
                    "config_name": "simplified",
                    "features": [
                        {"name": "text", "dtype": "string"},
                        {
                            "name": "labels",
                            "sequence": {
                                "class_label": {
                                    "names": {
                                        "0": "admiration",
                                        "1": "amusement",
                                        "2": "anger",
                                        "3": "annoyance",
                                        "4": "approval",
                                        "5": "caring",
                                        "6": "confusion",
                                        "7": "curiosity",
                                        "8": "desire",
                                        "9": "disappointment",
                                        "10": "disapproval",
                                        "11": "disgust",
                                        "12": "embarrassment",
                                        "13": "excitement",
                                        "14": "fear",
                                        "15": "gratitude",
                                        "16": "grief",
                                        "17": "joy",
                                        "18": "love",
                                        "19": "nervousness",
                                        "20": "optimism",
                                        "21": "pride",
                                        "22": "realization",
                                        "23": "relief",
                                        "24": "remorse",
                                        "25": "sadness",
                                        "26": "surprise",
                                        "27": "neutral",
                                    }
                                }
                            },
                        },
                    ],
                    "splits": [
                        {"name": "train", "num_examples": 2},
                        {"name": "validation", "num_examples": 1},
                        {"name": "test", "num_examples": 1},
                    ],
                }
            ],
        },
    }


def _write_meld_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Sr No.", "Utterance", "Speaker", "Emotion", "Sentiment", "Dialogue_ID", "Utterance_ID"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "Sr No.": "1",
                "Utterance": "Can you explain what happened?",
                "Speaker": "speaker",
                "Emotion": "neutral",
                "Sentiment": "neutral",
                "Dialogue_ID": "0",
                "Utterance_ID": "0",
            }
        )


def test_goemotions_license_gate_accepts_apache_2_metadata() -> None:
    metadata = validate_goemotions_metadata(_goemotions_metadata())

    assert metadata["license"] == "apache-2.0"
    assert metadata["splits"] == {"train": 2, "validation": 1, "test": 1}


def test_goemotions_license_gate_rejects_non_apache_metadata() -> None:
    try:
        validate_goemotions_metadata(_goemotions_metadata("cc-by"))
    except ValueError as exc:
        assert "apache-2.0" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected non-Apache GoEmotions metadata to fail")


def test_meld_gate_accepts_text_only_gpl3_local_source(tmp_path: Path) -> None:
    for filename in ("train_sent_emo.csv", "dev_sent_emo.csv", "test_sent_emo.csv"):
        _write_meld_csv(tmp_path / filename)

    metadata = validate_meld_metadata({"id": "declare-lab/MELD", "cardData": {"license": "gpl-3.0"}})
    manifest = build_meld_manifest(tmp_path, metadata)

    assert manifest["license_id"] == "gpl-3.0"
    assert manifest["local_only"] is True
    assert manifest["text_only"] is True
    assert manifest["audio_video_used"] is False
    assert manifest["commercial_training_allowed"] is False


def test_meld_gate_rejects_media_files(tmp_path: Path) -> None:
    for filename in ("train_sent_emo.csv", "dev_sent_emo.csv", "test_sent_emo.csv"):
        _write_meld_csv(tmp_path / filename)
    (tmp_path / "clip.mp4").write_bytes(b"not real media")

    metadata = validate_meld_metadata({"id": "declare-lab/MELD", "cardData": {"license": "gpl-3.0"}})
    try:
        build_meld_manifest(tmp_path, metadata)
    except ValueError as exc:
        assert "media files found" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected MELD media file to fail")


def test_meld_gate_rejects_missing_gpl3_metadata() -> None:
    try:
        validate_meld_metadata({"id": "declare-lab/MELD", "cardData": {"license": "apache-2.0"}})
    except ValueError as exc:
        assert "gpl-3.0" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected non-GPL MELD metadata to fail")
