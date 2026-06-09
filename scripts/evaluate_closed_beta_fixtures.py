#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vibesignal_ai.matching import match_conversation  # noqa: E402


CUE_ALIASES = {
    "unanswered_ask": {"answer_evasion_pattern"},
    "escalation": {"conflict", "escalation_risk", "repair_opportunity"},
    "cognitive_overload": {"cognitive_load", "overloaded_message"},
    "reassurance/directness": {"reassurance", "directness"},
    "reassurance_directness": {"reassurance", "directness"},
    "low_evidence": {"low_signal"},
}


def normalize_text(value: Any) -> str:
    return str(value or "").strip()


def normalize_key(value: Any) -> str:
    return normalize_text(value).lower().replace("-", "_").replace(" ", "_")


def read_fixtures(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("fixtures") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Closed-beta fixtures must be a list or an object with a fixtures list.")
    return rows


def fixture_errors(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in (
        "id",
        "synthetic",
        "not_copied_from_real_chat",
        "input",
        "expected_cue",
        "required_safe_phrases",
        "forbidden_outputs",
        "safe_output",
        "screenshot_allowed",
    ):
        if field not in row:
            errors.append(f"missing required field {field}")
    if row.get("synthetic") is not True:
        errors.append("synthetic must be true")
    if row.get("not_copied_from_real_chat") is not True:
        errors.append("not_copied_from_real_chat must be true")
    if not isinstance(row.get("required_safe_phrases", []), list):
        errors.append("required_safe_phrases must be a list")
    if not isinstance(row.get("forbidden_outputs", []), list):
        errors.append("forbidden_outputs must be a list")
    return errors


def parse_fixture_messages(text: str, fixture_id: str) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for index, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        author = "other" if len(messages) % 2 else "self"
        body = line
        if ":" in line:
            prefix, suffix = line.split(":", 1)
            prefix = prefix.strip().lower()
            if prefix in {"self", "me", "other", "them"}:
                author = "self" if prefix in {"self", "me"} else "other"
                body = suffix.strip()
        if body:
            messages.append(
                {
                    "id": f"{fixture_id}_m{index}",
                    "author": author,
                    "text": body,
                }
            )
    return messages


def collect_evidence_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in (
        "evidence",
        "inconsistency_cues",
        "unsupported_claim_shift",
        "specificity_drop",
        "answer_evasion_pattern",
        "contradiction_against_prior_message",
    ):
        value = result.get(key)
        if isinstance(value, list):
            rows.extend(row for row in value if isinstance(row, dict))
    return rows


def cue_families(result: dict[str, Any]) -> set[str]:
    families = {normalize_key(row.get("cue_family") or row.get("cue_id")) for row in collect_evidence_rows(result)}
    if result.get("low_signal_fallback") is True or normalize_key(result.get("result_state")) == "low_signal":
        families.add("low_signal")
    return {family for family in families if family}


def user_facing_output_text(result: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("safe_summary", "safe_explanation", "result_state", "signal_strength"):
        parts.append(normalize_text(result.get(key)))
    for key in ("cannot_infer", "safe_next_steps", "top_alignment_factors", "top_friction_factors"):
        value = result.get(key)
        if isinstance(value, list):
            parts.extend(normalize_text(item) for item in value)
    for row in collect_evidence_rows(result):
        parts.extend(
            normalize_text(row.get(key))
            for key in ("safe_phrase", "explanation", "repair_suggestion")
        )
    if result.get("low_signal_fallback") is True or normalize_key(result.get("result_state")) == "low_signal":
        parts.append("Not enough context to read safely.")
    return "\n".join(part for part in parts if part)


def expected_cue_hit(expected_cue: str, actual_families: set[str]) -> bool:
    expected = normalize_key(expected_cue)
    if not expected:
        return False
    allowed = CUE_ALIASES.get(expected, {expected})
    return bool(allowed & actual_families)


def expected_span_hit(expected_span: str, result: dict[str, Any]) -> bool:
    expected = normalize_text(expected_span).lower()
    if not expected:
        return True
    for row in collect_evidence_rows(result):
        haystack = "\n".join(
            normalize_text(row.get(key)).lower()
            for key in ("evidence_text", "safe_phrase", "explanation")
        )
        if expected in haystack:
            return True
    return False


def evaluate_fixture(row: dict[str, Any]) -> dict[str, Any]:
    fixture_id = normalize_text(row.get("id"))
    messages = parse_fixture_messages(normalize_text(row.get("input")), fixture_id)
    result = match_conversation({"conversation_id": fixture_id, "messages": messages})
    families = cue_families(result)
    output_text = user_facing_output_text(result)
    lowered_output = output_text.lower()
    required_phrases = [normalize_text(item) for item in row.get("required_safe_phrases", []) if normalize_text(item)]
    forbidden_outputs = [normalize_text(item) for item in row.get("forbidden_outputs", []) if normalize_text(item)]
    forbidden_hits = [phrase for phrase in forbidden_outputs if phrase.lower() in lowered_output]
    required_hits = [phrase for phrase in required_phrases if phrase.lower() in lowered_output]
    cue_hit = expected_cue_hit(normalize_text(row.get("expected_cue")), families)
    low_evidence = "low_signal" in families
    required_safe_phrase_hit = len(required_hits) == len(required_phrases)
    span_hit = expected_span_hit(normalize_text(row.get("expected_span")), result)
    return {
        "id": fixture_id,
        "synthetic": row.get("synthetic") is True,
        "expected_cue": normalize_text(row.get("expected_cue")),
        "actual_cues": sorted(families),
        "cue_hit": cue_hit,
        "expected_span_hit": span_hit,
        "required_safe_phrase_hit": required_safe_phrase_hit,
        "required_safe_phrase_hits": required_hits,
        "forbidden_output_violations": forbidden_hits,
        "low_evidence_fallback": low_evidence,
        "unclear_output": not cue_hit and not low_evidence and not required_safe_phrase_hit,
        "result_state": normalize_text(result.get("result_state")),
        "trained": False,
        "private_data_read": False,
    }


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = [evaluate_fixture(row) for row in rows]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "trained": False,
        "private_data_read": False,
        "source": "synthetic_closed_beta_fixtures",
        "summary": {
            "fixture_count": len(evaluated),
            "cue_hits": sum(1 for row in evaluated if row["cue_hit"]),
            "expected_span_hits": sum(1 for row in evaluated if row["expected_span_hit"]),
            "required_safe_phrase_hits": sum(1 for row in evaluated if row["required_safe_phrase_hit"]),
            "forbidden_output_violations": sum(
                len(row["forbidden_output_violations"]) for row in evaluated
            ),
            "low_evidence_fallbacks": sum(1 for row in evaluated if row["low_evidence_fallback"]),
            "unclear_outputs": sum(1 for row in evaluated if row["unclear_output"]),
        },
        "fixtures": evaluated,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Closed-Beta Synthetic Fixture Evaluation",
        "",
        f"- Generated: `{report['generated_at']}`",
        "- Training run: `false`",
        "- Private data read: `false`",
        f"- Fixtures: `{report['summary']['fixture_count']}`",
        f"- Cue hits: `{report['summary']['cue_hits']}`",
        f"- Expected span hits: `{report['summary']['expected_span_hits']}`",
        f"- Required safe phrase hits: `{report['summary']['required_safe_phrase_hits']}`",
        f"- Forbidden-output violations: `{report['summary']['forbidden_output_violations']}`",
        f"- Low-evidence fallbacks: `{report['summary']['low_evidence_fallbacks']}`",
        f"- Unclear outputs: `{report['summary']['unclear_outputs']}`",
        "",
        "| Fixture | Expected Cue | Cue Hit | Span Hit | Safe Phrase Hit | Forbidden Hits | Low Evidence |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["fixtures"]:
        lines.append(
            "| {id} | `{expected}` | `{cue}` | `{span}` | `{safe}` | `{forbidden}` | `{low}` |".format(
                id=row["id"],
                expected=row["expected_cue"],
                cue=str(row["cue_hit"]).lower(),
                span=str(row["expected_span_hit"]).lower(),
                safe=str(row["required_safe_phrase_hit"]).lower(),
                forbidden=len(row["forbidden_output_violations"]),
                low=str(row["low_evidence_fallback"]).lower(),
            )
        )
    lines.append("")
    lines.append("All fixture inputs are synthetic and marked `not_copied_from_real_chat=true`.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate closed-beta synthetic QA fixtures without training.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    rows = read_fixtures(input_path)
    errors = []
    for index, row in enumerate(rows, start=1):
        errors.extend(f"row {index} ({row.get('id', '<missing id>')}): {error}" for error in fixture_errors(row))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2

    report = build_report(rows)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    print(
        "Closed-beta fixture evaluation complete: "
        f"{report['summary']['fixture_count']} fixture(s), "
        f"{report['summary']['forbidden_output_violations']} forbidden-output violation(s), "
        "training=false, private_data_read=false."
    )
    return 1 if report["summary"]["forbidden_output_violations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
