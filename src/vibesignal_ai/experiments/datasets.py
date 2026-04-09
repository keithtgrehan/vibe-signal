"""Dataset conventions for local calibration experiments."""

from __future__ import annotations

from pathlib import Path


DATASET_LAYOUT = {
    "meld": {
        "root_dir": "MELD",
        "expected_files": ["train_sent_emo.csv", "dev_sent_emo.csv", "test_sent_emo.csv"],
        "license_note": "Use only with the dataset's original license and terms.",
    },
    "muse": {
        "root_dir": "MuSE",
        "expected_files": ["train.csv", "development.csv", "test.csv"],
        "license_note": "MuSE access and redistribution depend on the original dataset terms.",
    },
    "msp_podcast": {
        "root_dir": "MSP-Podcast",
        "expected_files": ["Partitions.txt", "Labels", "Audio"],
        "license_note": "MSP-Podcast usage depends on the original research license.",
    },
    "dailydialog": {
        "root_dir": "DailyDialog",
        "expected_files": ["dialogues_text.txt"],
        "license_note": "Future-support dataset only; keep separate from production paths.",
    },
    "goemotions": {
        "root_dir": "GoEmotions",
        "expected_files": ["train.tsv", "dev.tsv", "test.tsv"],
        "license_note": "Future-support dataset only; keep separate from production paths.",
    },
    "snli": {
        "root_dir": "SNLI",
        "expected_files": ["snli_1.0_train.jsonl"],
        "license_note": "Future-support dataset for optional NLI calibration only.",
    },
    "multinli": {
        "root_dir": "MultiNLI",
        "expected_files": ["multinli_1.0_train.jsonl"],
        "license_note": "Future-support dataset for optional NLI calibration only.",
    },
    "anli": {
        "root_dir": "ANLI",
        "expected_files": ["train.jsonl"],
        "license_note": "Future-support dataset for optional NLI calibration only.",
    },
}


def dataset_root(name: str, *, base_dir: str | Path | None = None) -> Path:
    base = Path(base_dir or "data").expanduser().resolve()
    spec = DATASET_LAYOUT.get(str(name).strip().lower())
    if spec is None:
        raise KeyError(f"unknown dataset: {name}")
    return base / spec["root_dir"]


def dataset_status(name: str, *, base_dir: str | Path | None = None) -> dict[str, object]:
    spec = DATASET_LAYOUT.get(str(name).strip().lower())
    if spec is None:
        raise KeyError(f"unknown dataset: {name}")
    root = dataset_root(name, base_dir=base_dir)
    expected = [root / entry for entry in spec["expected_files"]]
    return {
        "dataset": str(name).strip().lower(),
        "root": str(root),
        "present": root.exists(),
        "expected_files": [str(path) for path in expected],
        "available_files": [str(path) for path in expected if path.exists()],
        "license_note": spec["license_note"],
        "ready": all(path.exists() for path in expected),
    }
