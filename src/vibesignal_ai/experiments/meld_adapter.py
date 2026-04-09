"""MELD dataset scaffolding for local calibration work."""

from __future__ import annotations

from .datasets import dataset_status


def meld_setup_status(*, base_dir: str | None = None) -> dict[str, object]:
    status = dataset_status("meld", base_dir=base_dir)
    return {
        **status,
        "target_use": "emotion and dialogue-shift calibration experiments only",
        "production_path": False,
    }
