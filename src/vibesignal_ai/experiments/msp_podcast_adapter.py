"""MSP-Podcast dataset scaffolding for local calibration work."""

from __future__ import annotations

from .datasets import dataset_status


def msp_podcast_setup_status(*, base_dir: str | None = None) -> dict[str, object]:
    status = dataset_status("msp_podcast", base_dir=base_dir)
    return {
        **status,
        "target_use": "prosody and speech-structure calibration experiments only",
        "production_path": False,
    }
