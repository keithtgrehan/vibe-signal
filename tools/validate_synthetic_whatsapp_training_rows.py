#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SOURCE_TIER = "bronze_synthetic_whatsapp_10k"
SOURCE_TYPE = "synthetic_fixture"
RIGHTS_REVIEW_STATUS = "synthetic_only"
CONSENT_STATUS = "not_required_synthetic"

ALLOWED_CUES = {
    "directness",
    "specificity",
    "specificity_drop",
    "ambiguity",
    "unclear_ask",
    "hedging",
    "reassurance",
    "alignment",
    "pressure",
    "urgency",
    "boundary_pressure",
    "consent_clarity",
    "conflict",
    "escalation_risk",
    "repair_opportunity",
    "topic_shift",
    "answer_evasion_pattern",
    "cognitive_load",
    "overloaded_message",
    "contradiction_against_prior_message",
    "unsupported_claim_shift",
    "low_signal",
    "neutral",
}

BLOCKED_LABELS = {
    "attraction",
    "hidden_intent",
    "deception_certainty",
    "emotional_truth",
    "cheating",
    "diagnosis",
    "therapy_need",
    "neurotype",
    "attachment_style",
    "manipulation_claim",
    "abuse_certainty",
    "relationship_outcome",
    "gaslighting",
    "compatibility_prediction",
}

BLOCKED_INTERPRETATIONS = [
    "hidden_intent",
    "attraction",
    "deception_certainty",
    "diagnosis",
    "therapy",
    "manipulation_claim",
    "relationship_outcome",
]

FORBIDDEN_OUTPUTS = [
    "they like you",
    "they are lying",
    "this proves",
    "hidden intent",
    "gaslighting",
    "manipulating you",
    "diagnosis",
    "attachment style",
    "narcissist",
    "abusive person",
    "make them respond",
    "win them back",
]

FORBIDDEN_PUBLIC_CLAIM_PATTERNS = {
    "they_like_you": r"\bthey\s+like\s+you\b",
    "they_are_lying": r"\bthey\s+are\s+lying\b",
    "this_proves": r"\bthis\s+proves\b",
    "hidden_intent": r"\bhidden\s+intent\b",
    "gaslighting": r"\bgaslighting\b",
    "manipulating_you": r"\bmanipulat(?:ing|e|es|ion|ive)\s+you\b",
    "diagnosis": r"\bdiagnos(?:is|e|es|ing)\b",
    "therapy": r"\btherapy\b",
    "attachment_style": r"\battachment\s+style\b",
    "narcissist": r"\bnarcissist(?:ic)?\b",
    "abusive_person": r"\babusive\s+person\b",
    "make_them_respond": r"\bmake\s+them\s+respond\b",
    "win_them_back": r"\bwin\s+them\s+back\b",
    "deception_or_cheating": r"\b(?:deception|cheating|cheat|lying|lie\s+detector)\b",
    "neurotype": r"\b(?:neurotype|adhd|autis(?:m|tic))\b",
    "relationship_outcome": r"\brelationship\s+outcome\b",
}

MANIPULATION_NEXT_STEP_PATTERNS = {
    "make_them": r"\bmake\s+them\b",
    "win_them_back": r"\bwin\s+them\s+back\b",
    "pressure_reply": r"\bforce\s+(?:a\s+)?reply\b",
    "persuade": r"\bpersuad(?:e|ing)\b",
    "manipulate": r"\bmanipulat(?:e|es|ing|ion|ive)\b",
}

REAL_DATA_TEXT_PATTERNS = {
    "real_chat": r"\breal\s+(?:chat|conversation|message)\b",
    "private_chat": r"\bprivate\s+(?:chat|conversation|message|tester)\b",
    "tester_message": r"\btester\s+message\b",
    "provider_output": r"\b(?:openai|anthropic|groq|provider)\s+output\b",
    "external_dataset": r"\bexternal\s+dataset\b",
    "copied_from_real": r"\bcopied\s+from\s+real\b",
}

REQUIRED_ROW_FIELDS = {
    "row_id",
    "conversation_id",
    "source_tier",
    "source_type",
    "rights_review_status",
    "consent_status",
    "commercial_training_allowed",
    "research_training_allowed",
    "production_use_allowed",
    "model_quality_claims_allowed",
    "contains_raw_private_text",
    "contains_personal_data",
    "redaction_status",
    "review_status",
    "split",
    "scenario_family",
    "synthetic",
    "not_copied_from_real_chat",
    "messages",
    "text_for_training",
    "expected_cues",
    "evidence_spans",
    "blocked_interpretations",
    "forbidden_outputs",
    "safe_summary",
    "safe_next_step",
}

SPLITS = {"dev", "heldout", "hard_negative", "red_team", "unknown"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: row must be an object")
            rows.append(row)
    return rows


def _contains_pattern(text: str, patterns: dict[str, str]) -> list[str]:
    return [name for name, pattern in patterns.items() if re.search(pattern, text, flags=re.IGNORECASE)]


def _row_text_fields(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("scenario_family", "")),
        str(row.get("text_for_training", "")),
        str(row.get("safe_summary", "")),
        str(row.get("safe_next_step", "")),
    ]
    for message in row.get("messages", []) if isinstance(row.get("messages"), list) else []:
        if isinstance(message, dict):
            parts.append(str(message.get("text", "")))
    return "\n".join(parts)


def _validate_messages(index: int, row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    messages = row.get("messages")
    if not isinstance(messages, list) or not messages:
        return [f"row {index}: messages must be a non-empty list"]
    for message_index, message in enumerate(messages, start=1):
        if not isinstance(message, dict):
            errors.append(f"row {index}: message {message_index} must be an object")
            continue
        if str(message.get("speaker_role", "")) not in {"self", "other", "unknown"}:
            errors.append(f"row {index}: message {message_index} has invalid speaker_role")
        if not str(message.get("message_id", "")).strip():
            errors.append(f"row {index}: message {message_index} missing message_id")
        if not str(message.get("text", "")).strip():
            errors.append(f"row {index}: message {message_index} missing text")
    return errors


def validate_row(row: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_ROW_FIELDS - set(row))
    if missing:
        errors.append(f"row {index}: missing required fields: {', '.join(missing)}")
        return errors

    expected_literals = {
        "source_tier": SOURCE_TIER,
        "source_type": SOURCE_TYPE,
        "rights_review_status": RIGHTS_REVIEW_STATUS,
        "consent_status": CONSENT_STATUS,
        "redaction_status": "synthetic",
        "review_status": "synthetic_expected",
    }
    for field, expected in expected_literals.items():
        if row.get(field) != expected:
            errors.append(f"row {index}: {field} must be {expected!r}")

    required_booleans = {
        "commercial_training_allowed": False,
        "research_training_allowed": True,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "contains_raw_private_text": False,
        "contains_personal_data": False,
        "synthetic": True,
        "not_copied_from_real_chat": True,
    }
    for field, expected in required_booleans.items():
        if row.get(field) is not expected:
            errors.append(f"row {index}: {field} must be {expected}")

    if row.get("split") not in SPLITS:
        errors.append(f"row {index}: split must be one of {sorted(SPLITS)}")

    errors.extend(_validate_messages(index, row))
    text_for_training = str(row.get("text_for_training", ""))
    if not text_for_training.strip():
        errors.append(f"row {index}: text_for_training cannot be empty")

    cues = row.get("expected_cues")
    if not isinstance(cues, list) or not all(isinstance(cue, str) and cue for cue in cues):
        errors.append(f"row {index}: expected_cues must be a list of strings")
        cues = []
    else:
        for cue in cues:
            if cue in BLOCKED_LABELS:
                errors.append(f"row {index}: blocked label in expected_cues: {cue}")
            if cue not in ALLOWED_CUES:
                errors.append(f"row {index}: unsupported label in expected_cues: {cue}")

    evidence_spans = row.get("evidence_spans")
    if not isinstance(evidence_spans, list):
        errors.append(f"row {index}: evidence_spans must be a list")
        evidence_spans = []
    cue_set = set(cues)
    cue_positive_requires_evidence = bool(cue_set - {"low_signal", "neutral"})
    if cue_positive_requires_evidence and not evidence_spans:
        errors.append(f"row {index}: cue-positive rows require evidence spans")
    evidence_cues = set()
    for evidence_index, evidence in enumerate(evidence_spans, start=1):
        if not isinstance(evidence, dict):
            errors.append(f"row {index}: evidence span {evidence_index} must be an object")
            continue
        cue_type = str(evidence.get("cue_type", ""))
        span = str(evidence.get("span", ""))
        if cue_type not in cue_set:
            errors.append(f"row {index}: evidence span {evidence_index} cue_type {cue_type!r} not in expected_cues")
        if not span.strip():
            errors.append(f"row {index}: evidence span {evidence_index} missing span")
        elif span not in text_for_training:
            errors.append(f"row {index}: evidence span {evidence_index} does not appear in text_for_training")
        if not str(evidence.get("explanation", "")).strip():
            errors.append(f"row {index}: evidence span {evidence_index} missing explanation")
        evidence_cues.add(cue_type)
    for cue in cue_set - {"low_signal", "neutral"}:
        if cue not in evidence_cues:
            errors.append(f"row {index}: missing evidence span for cue {cue}")

    blocked_interpretations = row.get("blocked_interpretations")
    if not isinstance(blocked_interpretations, list) or not blocked_interpretations:
        errors.append(f"row {index}: blocked_interpretations must be a non-empty list")
    else:
        missing_blocked = set(BLOCKED_INTERPRETATIONS) - set(str(item) for item in blocked_interpretations)
        if missing_blocked:
            errors.append(f"row {index}: blocked_interpretations missing {sorted(missing_blocked)}")

    forbidden_outputs = row.get("forbidden_outputs")
    if not isinstance(forbidden_outputs, list) or not forbidden_outputs:
        errors.append(f"row {index}: forbidden_outputs must be a non-empty list")
    else:
        missing_forbidden = set(FORBIDDEN_OUTPUTS) - set(str(item) for item in forbidden_outputs)
        if missing_forbidden:
            errors.append(f"row {index}: forbidden_outputs missing {sorted(missing_forbidden)}")

    summary_hits = _contains_pattern(str(row.get("safe_summary", "")), FORBIDDEN_PUBLIC_CLAIM_PATTERNS)
    if summary_hits:
        errors.append(f"row {index}: safe_summary contains forbidden claim pattern(s): {summary_hits}")
    next_step = str(row.get("safe_next_step", ""))
    next_step_hits = _contains_pattern(next_step, FORBIDDEN_PUBLIC_CLAIM_PATTERNS | MANIPULATION_NEXT_STEP_PATTERNS)
    if next_step_hits:
        errors.append(f"row {index}: safe_next_step contains unsafe claim or tactic pattern(s): {next_step_hits}")

    data_hits = _contains_pattern(_row_text_fields(row), REAL_DATA_TEXT_PATTERNS)
    if data_hits:
        errors.append(f"row {index}: row text appears to reference non-synthetic or private data: {data_hits}")

    return errors


def validate_rows(rows: list[dict[str, Any]], manifest: dict[str, Any], *, allow_partial_sample: bool = False) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if manifest.get("source_tier") != SOURCE_TIER:
        errors.append("manifest source_tier must be bronze_synthetic_whatsapp_10k")
    if manifest.get("synthetic") is not True:
        errors.append("manifest synthetic must be true")
    expected_count = manifest.get("row_count")
    if not isinstance(expected_count, int) or expected_count < 0:
        errors.append("manifest row_count must be a non-negative integer")
    elif len(rows) != expected_count and not allow_partial_sample:
        errors.append(f"row count mismatch: input has {len(rows)} row(s), manifest expects {expected_count}")

    seen_ids: set[str] = set()
    cue_counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    evidence_count = 0
    for index, row in enumerate(rows, start=1):
        row_id = str(row.get("row_id", ""))
        if row_id in seen_ids:
            errors.append(f"row {index}: duplicate row_id {row_id}")
        seen_ids.add(row_id)
        errors.extend(validate_row(row, index))
        split_counts[str(row.get("split", "unknown"))] += 1
        for cue in row.get("expected_cues", []) if isinstance(row.get("expected_cues"), list) else []:
            cue_counts[str(cue)] += 1
        evidence_count += len(row.get("evidence_spans", []) if isinstance(row.get("evidence_spans"), list) else [])

    summary = {
        "status": "valid" if not errors else "invalid",
        "row_count": len(rows),
        "expected_row_count": expected_count,
        "split_counts": dict(sorted(split_counts.items())),
        "cue_counts": dict(sorted(cue_counts.items())),
        "evidence_span_count": evidence_count,
        "errors": errors,
    }
    return errors, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate synthetic WhatsApp pattern-recognition training rows.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--allow-partial-sample", action="store_true")
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    try:
        rows = read_jsonl(Path(args.input))
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        errors, summary = validate_rows(rows, manifest, allow_partial_sample=args.allow_partial_sample)
    except Exception as exc:
        summary = {"status": "invalid", "row_count": 0, "errors": [str(exc)]}
        errors = summary["errors"]

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if errors:
        print(f"Synthetic WhatsApp training-row validation failed: {len(errors)} error(s).", file=sys.stderr)
        for error in errors[:100]:
            print(f"- {error}", file=sys.stderr)
        if len(errors) > 100:
            print(f"- ... {len(errors) - 100} more error(s)", file=sys.stderr)
        return 1

    print(
        f"Synthetic WhatsApp training-row validation passed: "
        f"{summary['row_count']} row(s), {summary['evidence_span_count']} evidence span(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
