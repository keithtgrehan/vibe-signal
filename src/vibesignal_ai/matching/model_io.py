"""I/O helpers for research-only Vibe matching baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MATCHING_LABELS = (
    "clarity_fit",
    "boundary_fit",
    "repair_fit",
    "communication_fit",
    "pressure_risk",
    "cognitive_load_fit",
    "inconsistency_cues",
    "unsupported_claim_shift",
    "specificity_drop",
    "answer_evasion_pattern",
    "contradiction_against_prior_message",
)


def load_match_pairs(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(row)
    return rows


def pair_text(row: dict[str, Any]) -> str:
    return f"{row.get('text_a', '')} [PAIR] {row.get('text_b', '')}"


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_baseline_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Vibe Matching Baseline Evaluation",
        "",
        "Synthetic-only research baseline. These metrics do not support public model-quality claims.",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Project mode: `{report.get('project_mode')}`",
        f"- Row count: `{report.get('row_count')}`",
        f"- Source: `{report.get('source_id', 'synthetic_vibe_matching')}`",
        f"- Split strategy: `{(report.get('split') or {}).get('strategy', 'not_reported')}`",
        f"- Benchmark scope: `{report.get('benchmark_scope', 'synthetic_only')}`",
        f"- Provider calls made: `{report.get('provider_calls_made')}`",
        f"- Model artifacts saved: `{report.get('model_artifacts_saved')}`",
        f"- Public quality claims supported: `{report.get('public_quality_claims_supported', False)}`",
        "",
        "## Metrics",
        "",
        "| Label | Accuracy | Precision | Recall | F1 | Trained |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    metrics = report.get("metrics_by_label", {})
    if isinstance(metrics, dict):
        for label in MATCHING_LABELS:
            row = metrics.get(label, {})
            lines.append(
                "| {label} | {accuracy:.3f} | {precision:.3f} | {recall:.3f} | {f1:.3f} | {trained} |".format(
                    label=label,
                    accuracy=float(row.get("accuracy", 0.0) or 0.0),
                    precision=float(row.get("precision", 0.0) or 0.0),
                    recall=float(row.get("recall", 0.0) or 0.0),
                    f1=float(row.get("f1", 0.0) or 0.0),
                    trained=str(bool(row.get("trained", False))).lower(),
                )
            )
    lines.extend(
        [
            "",
            "## Limits",
            "",
            "- Synthetic-only fixtures are useful for harness checks, not real-world quality claims.",
            "- Template-category holdout is still synthetic-only and does not prove generalization.",
            "- Confidence and scores describe analysis quality and observable communication patterns only.",
            "- No deception, attraction, diagnosis, hidden-intent, or relationship-success model is built.",
        ]
    )
    return "\n".join(lines) + "\n"
