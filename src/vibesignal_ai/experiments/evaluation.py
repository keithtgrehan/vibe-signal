"""Lightweight evaluation harness for local experiment rows."""

from __future__ import annotations

from typing import Any


def summarize_experiment_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    if total == 0:
        return {
            "row_count": 0,
            "label_count": 0,
            "labels": {},
            "notes": ["No experiment rows were provided."],
        }

    labels: dict[str, int] = {}
    for row in rows:
        label = str(row.get("label", "unknown")).strip() or "unknown"
        labels[label] = labels.get(label, 0) + 1

    return {
        "row_count": total,
        "label_count": len(labels),
        "labels": labels,
        "notes": [
            "This is experiment scaffolding only.",
            "Use local datasets and explicit calibration notebooks or scripts outside the production path.",
        ],
    }
