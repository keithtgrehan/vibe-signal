#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vibesignal_ai.evidence.export import load_evidence_jsonl  # noqa: E402
from vibesignal_ai.evidence.objects import validate_evidence_object  # noqa: E402
from vibesignal_ai.safety.redline_output_blocker import check_output_text  # noqa: E402
from vibesignal_ai.safety.validator import validate_text  # noqa: E402


CLAIM_PATTERNS = {
    "ml_or_benchmark": ("ml", "machine learning", "benchmark claim", "benchmark-quality", "benchmark quality"),
    "retrieval_quality": ("retrieval quality", "retrieval-quality"),
    "model_quality": ("model quality", "model-quality", "production model"),
    "statistical_significance": ("statistical significance", "statistically significant", "p-value"),
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(row)
    return rows


def _strings(payload: Any) -> list[str]:
    if isinstance(payload, str):
        return [payload]
    if isinstance(payload, dict):
        values: list[str] = []
        for value in payload.values():
            values.extend(_strings(value))
        return values
    if isinstance(payload, list):
        values: list[str] = []
        for value in payload:
            values.extend(_strings(value))
        return values
    return []


def load_output_payloads(path: Path | None) -> list[Any]:
    if path is None:
        return []
    if path.suffix.lower() == ".jsonl":
        return load_jsonl(path)
    if path.suffix.lower() == ".json":
        return [json.loads(path.read_text(encoding="utf-8"))]
    return [path.read_text(encoding="utf-8")]


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def evaluate(
    *,
    gold_labels: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
    output_payloads: list[Any] | None = None,
) -> dict[str, Any]:
    output_payloads = output_payloads or []
    output_texts = [text for payload in output_payloads for text in _strings(payload)]

    evidence_errors = [
        f"row {index}: {error}"
        for index, row in enumerate(evidence_rows, start=1)
        for error in validate_evidence_object(row)
    ]
    evidence_texts = {str(row.get("evidence_text", "")) for row in evidence_rows}
    reviewed_label_count = len(gold_labels)
    matched_labels = 0
    missing_evidence = 0
    for row in gold_labels:
        evidence_text = str(row.get("evidence_text", "")).strip()
        if row.get("label_type") == "neutral":
            continue
        if not evidence_text:
            missing_evidence += 1
        elif evidence_text in evidence_texts:
            matched_labels += 1
        else:
            missing_evidence += 1

    output_errors = [error for text in output_texts for error in validate_text(text)]
    redline_results = [check_output_text(text) for text in output_texts]
    blocked_output_count = sum(1 for result in redline_results if result["status"] == "block")

    provider_canonical = 0
    for payload in output_payloads:
        rows = payload if isinstance(payload, list) else [payload]
        for row in rows:
            if not isinstance(row, dict):
                continue
            source_text = " ".join(str(row.get(field, "")) for field in ("source_type", "canonical_source", "provider"))
            if row.get("is_canonical") is True and "provider" in source_text.lower():
                provider_canonical += 1

    evidence_override_count = sum(1 for row in evidence_rows if row.get("deterministic_output_override_allowed") is True)

    claim_hits: dict[str, int] = {}
    for claim_name, needles in CLAIM_PATTERNS.items():
        claim_hits[claim_name] = sum(1 for text in output_texts if _contains_any(text, needles))

    blockers: list[str] = []
    if evidence_errors:
        blockers.append("evidence objects failed validation")
    if output_errors:
        blockers.append("unsafe output claim detected")
    if reviewed_label_count < 50 and claim_hits["ml_or_benchmark"]:
        blockers.append("below 50 reviewed labels: no ML/benchmark claims")
    if reviewed_label_count < 100 and claim_hits["retrieval_quality"]:
        blockers.append("below 100 reviewed labels: no retrieval-quality claims")
    if reviewed_label_count < 500 and claim_hits["model_quality"]:
        blockers.append("below 500 reviewed labels: no model-quality claims")
    if claim_hits["statistical_significance"]:
        blockers.append("no statistical-significance language")
    if provider_canonical:
        blockers.append("provider outputs cannot be canonical")
    if evidence_override_count:
        blockers.append("evidence objects cannot override deterministic outputs")

    return {
        "status": "pass" if not blockers else "fail",
        "metrics": {
            "reviewed_label_count": reviewed_label_count,
            "matched_labels": matched_labels,
            "unmatched_labels": max(0, reviewed_label_count - matched_labels),
            "potential_false_positives": max(0, len(evidence_rows) - matched_labels),
            "missing_evidence": missing_evidence,
            "unsupported_claim_count": len(output_errors) + claim_hits["statistical_significance"],
            "blocked_output_count": blocked_output_count,
        },
        "claim_hits": claim_hits,
        "blockers": blockers,
        "evidence_errors": evidence_errors,
        "provider_canonical_count": provider_canonical,
        "evidence_override_count": evidence_override_count,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate Vibe review/evidence outputs against launch-safety gates.")
    parser.add_argument("--gold-labels", help="Reviewed gold-label JSONL path.")
    parser.add_argument("--evidence", help="Evidence objects JSONL path.")
    parser.add_argument("--outputs", help="Optional JSON/JSONL/text output payload path to scan for claims.")
    parser.add_argument("--json-out", help="Optional JSON report path.")
    args = parser.parse_args(argv)

    gold_labels = load_jsonl(Path(args.gold_labels)) if args.gold_labels else []
    evidence_rows = load_evidence_jsonl(args.evidence) if args.evidence else []
    output_payloads = load_output_payloads(Path(args.outputs)) if args.outputs else []
    report = evaluate(gold_labels=gold_labels, evidence_rows=evidence_rows, output_payloads=output_payloads)

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
