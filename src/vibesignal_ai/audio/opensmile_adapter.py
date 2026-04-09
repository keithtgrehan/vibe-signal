"""Optional openSMILE adapter for structured acoustic summaries."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

HAS_OPENSMILE = True
try:  # pragma: no cover - optional dependency
    import opensmile
except Exception:  # pragma: no cover - optional dependency
    HAS_OPENSMILE = False
    opensmile = None


def opensmile_available() -> bool:
    return HAS_OPENSMILE and opensmile is not None


@lru_cache(maxsize=4)
def _build_smile(feature_set_name: str = "eGeMAPSv02", level_name: str = "Functionals"):
    if not opensmile_available():
        return None
    try:
        feature_set = getattr(opensmile.FeatureSet, feature_set_name)
        feature_level = getattr(opensmile.FeatureLevel, level_name)
        return opensmile.Smile(feature_set=feature_set, feature_level=feature_level)
    except Exception:  # pragma: no cover - environment specific
        return None


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _collect_metric_values(frame: Any, patterns: tuple[str, ...]) -> list[float]:
    columns = [str(column) for column in getattr(frame, "columns", [])]
    collected: list[float] = []
    for column in columns:
        lowered = column.lower()
        if not any(pattern in lowered for pattern in patterns):
            continue
        try:
            series = frame[column]
            collected.append(float(series.mean()))
        except Exception:
            continue
    return collected


def _frame_summary(frame: Any) -> dict[str, float]:
    if frame is None or getattr(frame, "empty", True):
        return {}
    return {
        "energy_intensity_proxy": round(_mean(_collect_metric_values(frame, ("loudness", "energy", "pcm_rmsenergy"))), 4),
        "voicing_ratio_proxy": round(_mean(_collect_metric_values(frame, ("voicing", "voiceprob", "f0finalclipped"))), 4),
        "pitch_variation_proxy": round(_mean(_collect_metric_values(frame, ("f0", "pitch"))), 4),
        "spectral_flux_proxy": round(_mean(_collect_metric_values(frame, ("spectralflux", "alpha", "slope"))), 4),
        "hesitation_support_proxy": round(_mean(_collect_metric_values(frame, ("jitter", "shimmer", "pause"))), 4),
    }


def _segment_frame(frame: Any, start_time_s: float, end_time_s: float) -> Any:
    if frame is None or getattr(frame, "empty", True):
        return None
    index = getattr(frame, "index", None)
    if index is None or getattr(index, "nlevels", 0) < 2:
        return None
    try:
        start_values = index.get_level_values(1)
        end_values = index.get_level_values(2) if index.nlevels >= 3 else start_values
        mask = [
            float(getattr(start, "total_seconds", lambda: start)()) < float(end_time_s)
            and float(getattr(end, "total_seconds", lambda: end)()) > float(start_time_s)
            for start, end in zip(start_values, end_values)
        ]
        subset = frame.loc[mask]
        return subset if not getattr(subset, "empty", True) else None
    except Exception:  # pragma: no cover - frame shape specific
        return None


def extract_opensmile_features(
    audio_path: str | Path,
    *,
    segments: list[dict[str, Any]] | None = None,
    enabled: bool = False,
    feature_set_name: str = "eGeMAPSv02",
    level_name: str = "Functionals",
) -> dict[str, Any]:
    path = Path(audio_path).expanduser().resolve()
    if not enabled:
        return {
            "enabled": False,
            "available": False,
            "backend": "disabled",
            "feature_set": feature_set_name,
            "feature_level": level_name,
            "summary": {},
            "segment_features": [],
        }
    if not path.exists() or not opensmile_available():
        return {
            "enabled": True,
            "available": False,
            "backend": "unavailable",
            "feature_set": feature_set_name,
            "feature_level": level_name,
            "summary": {},
            "segment_features": [],
        }

    smile = _build_smile(feature_set_name, level_name)
    if smile is None:
        return {
            "enabled": True,
            "available": False,
            "backend": "unavailable",
            "feature_set": feature_set_name,
            "feature_level": level_name,
            "summary": {},
            "segment_features": [],
        }

    try:
        frame = smile.process_file(str(path))
    except Exception:  # pragma: no cover - environment specific
        return {
            "enabled": True,
            "available": False,
            "backend": "runtime_error",
            "feature_set": feature_set_name,
            "feature_level": level_name,
            "summary": {},
            "segment_features": [],
        }

    segment_features: list[dict[str, Any]] = []
    for segment in segments or []:
        start_time_s = float(segment.get("start", 0.0) or 0.0)
        end_time_s = float(segment.get("end", start_time_s) or start_time_s)
        subset = _segment_frame(frame, start_time_s, end_time_s)
        if subset is None:
            continue
        metrics = _frame_summary(subset)
        if not any(metrics.values()):
            continue
        segment_features.append(
            {
                "segment_id": int(segment.get("segment_id", len(segment_features) + 1)),
                **metrics,
            }
        )

    return {
        "enabled": True,
        "available": True,
        "backend": "opensmile",
        "feature_set": feature_set_name,
        "feature_level": level_name,
        "summary": _frame_summary(frame),
        "segment_features": segment_features,
    }
