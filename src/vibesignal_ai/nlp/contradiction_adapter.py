"""Optional local NLI adapter for statement-relation support."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

HAS_TRANSFORMERS = True
try:  # pragma: no cover - optional dependency
    from transformers import pipeline
except Exception:  # pragma: no cover - optional dependency
    HAS_TRANSFORMERS = False
    pipeline = None

from ..config.runtime_flags import NLI_MODEL_NAME


def nli_available() -> bool:
    return HAS_TRANSFORMERS and pipeline is not None


@lru_cache(maxsize=2)
def _load_nli_pipeline(model_name: str = NLI_MODEL_NAME):
    if not nli_available():
        return None
    try:
        return pipeline(
            "text-classification",
            model=model_name,
            tokenizer=model_name,
            local_files_only=True,
        )
    except Exception:  # pragma: no cover - local model availability specific
        return None


def _safe_fallback(*, enabled: bool, model_name: str, backend: str) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "available": False,
        "backend": backend,
        "model_name": model_name,
        "relation": "unavailable",
        "scores": {},
    }


def _map_relation(label: str) -> str:
    lowered = str(label or "").lower()
    if "contrad" in lowered:
        return "contradiction_signal"
    if "entail" in lowered or "align" in lowered:
        return "aligned_statement_relation"
    return "neutral_relation"


def score_statement_relation(
    premise: str,
    hypothesis: str,
    *,
    enabled: bool = False,
    model_name: str = NLI_MODEL_NAME,
) -> dict[str, Any]:
    left = str(premise or "").strip()
    right = str(hypothesis or "").strip()
    if not enabled:
        return _safe_fallback(enabled=False, model_name=model_name, backend="disabled")
    if not left or not right or not nli_available():
        return _safe_fallback(enabled=True, model_name=model_name, backend="unavailable")

    classifier = _load_nli_pipeline(model_name)
    if classifier is None:
        return _safe_fallback(enabled=True, model_name=model_name, backend="unavailable")

    try:
        raw = classifier({"text": left, "text_pair": right}, top_k=None)
    except Exception:  # pragma: no cover - runtime/model specific
        return _safe_fallback(enabled=True, model_name=model_name, backend="runtime_error")

    results = raw[0] if isinstance(raw, list) and raw and isinstance(raw[0], list) else raw
    if not isinstance(results, list):
        results = [results]

    scores: dict[str, float] = {}
    top_label = ""
    top_score = -1.0
    for item in results:
        label = str(item.get("label", "")).strip()
        score = float(item.get("score", 0.0) or 0.0)
        relation = _map_relation(label)
        scores[relation] = max(score, scores.get(relation, 0.0))
        if score > top_score:
            top_label = label
            top_score = score

    return {
        "enabled": True,
        "available": True,
        "backend": "transformers_local",
        "model_name": model_name,
        "relation": _map_relation(top_label),
        "scores": {key: round(value, 4) for key, value in scores.items()},
    }
