"""MuSE dataset scaffolding for local calibration work."""

from __future__ import annotations

from .datasets import dataset_status


def muse_setup_status(*, base_dir: str | None = None) -> dict[str, object]:
    status = dataset_status("muse", base_dir=base_dir)
    return {
        **status,
        "target_use": "multimodal speech-emotion and hesitation calibration experiments only",
        "production_path": False,
    }
