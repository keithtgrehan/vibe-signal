#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))


DEFAULT_OUT_DIR = REPO_ROOT / "data" / "synthetic" / "whatsapp"
DEFAULT_ENGINE_REPORT_DIR = REPO_ROOT / "reports" / "engine_eval"
DEFAULT_SEED = 20260603
SIGNAL_STRENGTHS = {"strong", "medium", "low", "mixed", "insufficient"}
CUE_UNIVERSE = (
    "alignment",
    "ambiguity",
    "answer_evasion_pattern",
    "boundary_pressure",
    "cognitive_load",
    "conflict",
    "contradiction_against_prior_message",
    "directness",
    "escalation_risk",
    "hedging",
    "overloaded_message",
    "pressure",
    "reassurance",
    "repair_opportunity",
    "specificity",
    "specificity_drop",
    "topic_shift",
    "unclear_ask",
    "urgency",
    "unsupported_claim_shift",
)
FORBIDDEN_OUTPUT_PATTERNS = (
    r"\bsecretly\b",
    r"\bthey\s+like\s+you\b",
    r"\bhidden\s+intent\b",
    r"\bdetects?\s+cheating\b",
    r"\bcheating\s+detector\b",
    r"\b(?:lied|lying|detects?\s+lies?)\b",
    r"\bdiagnos",
    r"\bnarcissist\b",
    r"\battachment\s+style\b",
    r"\badhd\b",
    r"\bautis",
    r"\bmanipulat",
    r"\bmake\s+them\b",
    r"\bwin\s+them\s+back\b",
    r"\bguaranteed\b",
    r"\bthis\s+proves\b",
    r"\bemotional\s+truth\b",
)


@dataclass(frozen=True)
class Template:
    category: str
    expected_cues: tuple[str, ...]
    expected_signal_strength: str
    messages: tuple[tuple[str, str], ...]
    notes: str


TEMPLATES: tuple[Template, ...] = (
    Template(
        "happy",
        ("directness", "specificity", "reassurance"),
        "medium",
        (
            ("self", "Can you confirm Friday at 3pm?"),
            ("other", "Yes, Friday at 3pm works. No pressure if we need to adjust."),
        ),
        "Clear synthetic planning exchange.",
    ),
    Template(
        "new_in_love",
        ("directness", "specificity", "reassurance"),
        "medium",
        (
            ("self", "Could you confirm Saturday lunch for a longer check-in? No rush if not."),
            ("other", "Saturday lunch works, and we can keep it simple."),
        ),
        "Warm synthetic exchange; category metadata is not a claim about private feelings.",
    ),
    Template(
        "in_love",
        ("directness", "specificity", "alignment"),
        "medium",
        (
            ("self", "Would you like to cook dinner Friday at 7?"),
            ("other", "Yes, Friday at 7 works and that plan sounds good."),
        ),
        "Supportive synthetic exchange; category metadata is not a claim about private feelings.",
    ),
    Template(
        "unhappy",
        ("ambiguity", "answer_evasion_pattern", "conflict"),
        "mixed",
        (
            ("self", "Can we talk tonight about the plan?"),
            ("other", "Maybe later, whatever. Anyway, I am frustrated."),
        ),
        "Synthetic tension example using observable wording only.",
    ),
    Template(
        "scared",
        ("pressure", "boundary_pressure", "urgency"),
        "mixed",
        (
            ("self", "I cannot share my location tonight."),
            ("other", "You have to send me your location right now."),
        ),
        "Synthetic boundary-pressure example.",
    ),
    Template(
        "low_signal",
        (),
        "insufficient",
        (
            ("self", "ok"),
            ("other", "maybe"),
        ),
        "Short synthetic exchange expected to trigger low-signal fallback.",
    ),
    Template(
        "boundary_pressure",
        ("pressure", "boundary_pressure"),
        "mixed",
        (
            ("self", "I said I am not available tonight."),
            ("other", "You have to answer right now and explain why."),
        ),
        "Synthetic pressure after a boundary statement.",
    ),
    Template(
        "conflict_repair",
        ("conflict", "repair_opportunity", "unsupported_claim_shift"),
        "mixed",
        (
            ("self", "I am frustrated because you always make the schedule harder."),
            ("self", "Sorry, let me rephrase the ask."),
        ),
        "Synthetic conflict plus repair opening.",
    ),
    Template(
        "overloaded_message",
        ("directness", "cognitive_load", "overloaded_message"),
        "mixed",
        (
            ("self", "Can you confirm the time, the place, the backup plan, whether you saw the note, whether I should bring the printed copy, whether the earlier plan still works, and whether there is anything else I should prepare before tomorrow?"),
            ("other", "Can you send one request first so I can answer clearly?"),
        ),
        "Synthetic dense multi-ask message.",
    ),
    Template(
        "cheating_ambiguous",
        (
            "ambiguity",
            "answer_evasion_pattern",
            "specificity_drop",
            "contradiction_against_prior_message",
            "escalation_risk",
            "repair_opportunity",
        ),
        "mixed",
        (
            ("other", "I can meet Friday at 7pm."),
            ("self", "Can you confirm Friday at 7pm and the place?"),
            ("other", "Maybe later. Anyway."),
            ("other", "I can't meet Friday. You have to stop asking because I am frustrated. Sorry, let me rephrase."),
        ),
        "Private synthetic evaluation metadata only. This category must never be described as product ability or cheating detection.",
    ),
)


def _message_text(text: str, fixture_index: int) -> str:
    return f"{text} [synthetic fixture {fixture_index}]"


def build_conversations(target_messages: int, *, seed: int = DEFAULT_SEED) -> list[dict[str, Any]]:
    """Build deterministic synthetic WhatsApp-style conversations.

    The seed is recorded in fixture metadata and used by API evaluation selection.
    Fixture text is generated from hand-authored synthetic templates only.
    """

    if target_messages < 2:
        raise ValueError("messages must be at least 2")
    conversations: list[dict[str, Any]] = []
    total_messages = 0
    fixture_index = 1
    while total_messages < target_messages:
        added_this_cycle = False
        for template in TEMPLATES:
            message_count = len(template.messages)
            if total_messages + message_count > target_messages:
                continue
            fixture_id = f"synthetic_whatsapp_{fixture_index:05d}"
            messages = [
                {
                    "id": f"m{offset}",
                    "author": author,
                    "created_at": f"2026-06-03T09:{(fixture_index + offset) % 60:02d}:00Z",
                    "text": _message_text(text, fixture_index),
                }
                for offset, (author, text) in enumerate(template.messages, start=1)
            ]
            conversations.append(
                {
                    "fixture_id": fixture_id,
                    "source_type": "synthetic_fixture",
                    "synthetic": True,
                    "not_copied_from_real_chat": True,
                    "seed": int(seed),
                    "category": template.category,
                    "category_scope": (
                        "private synthetic evaluation metadata only"
                        if template.category == "cheating_ambiguous"
                        else "synthetic regression metadata"
                    ),
                    "input_text": "\n".join(message["text"] for message in messages),
                    "message_count": len(messages),
                    "messages": messages,
                    "expected_result_type": "low_signal" if template.category == "low_signal" else "pattern_review",
                    "expected_cues": list(template.expected_cues),
                    "expected_evidence_spans": [
                        {
                            "cue": cue,
                            "require_evidence_text": True,
                            "require_offsets": True,
                        }
                        for cue in template.expected_cues
                    ],
                    "expected_signal_strength": template.expected_signal_strength,
                    "expected_cannot_infer": [
                        "private feelings or motives",
                        "deception verdicts or private context",
                        "health, identity, or relationship labels",
                    ],
                    "forbidden_outputs": list(FORBIDDEN_OUTPUT_PATTERNS),
                    "safe_repair_suggestion": "Use a short clarification that respects boundaries and leaves room to pause.",
                    "notes": template.notes,
                }
            )
            total_messages += message_count
            fixture_index += 1
            added_this_cycle = True
            if total_messages == target_messages:
                break
        if not added_this_cycle:
            raise ValueError(f"could not generate exactly {target_messages} messages with the available templates")
    return conversations


def select_for_api_regression(conversations: list[dict[str, Any]], *, limit: int | None, seed: int) -> list[dict[str, Any]]:
    if limit is None or limit >= len(conversations):
        return list(conversations)
    if limit <= 0:
        raise ValueError("limit must be positive when provided")

    rng = random.Random(int(seed))
    by_category: dict[str, list[dict[str, Any]]] = {}
    for row in conversations:
        by_category.setdefault(str(row["category"]), []).append(row)
    for rows in by_category.values():
        rng.shuffle(rows)

    categories = sorted(by_category)
    rng.shuffle(categories)
    selected: list[dict[str, Any]] = []
    while len(selected) < limit:
        made_progress = False
        for category in categories:
            rows = by_category.get(category) or []
            if rows:
                selected.append(rows.pop(0))
                made_progress = True
                if len(selected) == limit:
                    break
        if not made_progress:
            break
    return sorted(selected, key=lambda row: str(row["fixture_id"]))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def normalize_api_url(value: str) -> str:
    candidate = str(value or "").strip().rstrip("/")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("api_url_must_be_http_or_https_origin")
    if parsed.username or parsed.password or parsed.params or parsed.query or parsed.fragment:
        raise ValueError("api_url_must_not_include_credentials_query_or_fragment")
    if parsed.path not in {"", "/"}:
        raise ValueError("api_url_must_be_origin_without_path")
    return f"{parsed.scheme}://{parsed.netloc}"


def analyze_payload_for(conversation: dict[str, Any]) -> dict[str, Any]:
    return {
        "conversation_id": conversation["fixture_id"],
        "messages": conversation["messages"],
        "source_type": "synthetic_fixture",
        "synthetic": True,
        "not_copied_from_real_chat": True,
        "evaluation_context": {
            "category": conversation["category"],
            "category_scope": conversation["category_scope"],
            "expected_result_type": conversation["expected_result_type"],
        },
    }


def _api_analyze(api_url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    url = normalize_api_url(api_url) + "/api/analyze"
    request = Request(
        url,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - operator supplies backend URL.
        parsed = json.loads(response.read(128_000).decode("utf-8", errors="replace"))
    if not isinstance(parsed, dict):
        raise RuntimeError("api analyze result must be an object")
    return parsed


def _safe_user_facing_text(result: dict[str, Any]) -> str:
    values: list[str] = [
        str(result.get("safe_summary", "")),
        str(result.get("safe_explanation", "")),
        *(str(item) for item in result.get("positive_factors", []) if isinstance(item, str)),
        *(str(item) for item in result.get("risk_factors", []) if isinstance(item, str)),
        *(str(item) for item in result.get("cannot_infer", []) if isinstance(item, str)),
        *(str(item) for item in result.get("safe_next_steps", []) if isinstance(item, str)),
    ]
    for field in (
        "evidence",
        "inconsistency_cues",
        "unsupported_claim_shift",
        "specificity_drop",
        "answer_evasion_pattern",
        "contradiction_against_prior_message",
    ):
        for item in result.get(field, []) or []:
            if isinstance(item, dict):
                values.append(str(item.get("safe_phrase", "")))
                values.append(str(item.get("explanation", "")))
                values.append(str(item.get("repair_suggestion", "")))
    return " ".join(values)


def _observed_cues(result: dict[str, Any]) -> set[str]:
    cues: set[str] = set()
    for field in (
        "evidence",
        "inconsistency_cues",
        "unsupported_claim_shift",
        "specificity_drop",
        "answer_evasion_pattern",
        "contradiction_against_prior_message",
    ):
        for item in result.get(field, []) or []:
            if isinstance(item, dict):
                cue = str(item.get("cue_id") or item.get("cue_family") or item.get("cue_name") or "").strip()
                if cue:
                    cues.add(cue)
    return cues


def _signal_strength(result: dict[str, Any]) -> str:
    value = str(result.get("signal_strength", "")).strip()
    if value:
        return value
    state = str(result.get("signal_state", result.get("result_state", ""))).strip()
    if state == "low_signal":
        return "insufficient"
    if state == "ready":
        return "low"
    return ""


def _low_signal_fallback(result: dict[str, Any]) -> bool:
    if "low_signal_fallback" in result:
        return result.get("low_signal_fallback") is True
    return str(result.get("signal_state", result.get("result_state", ""))).strip() == "low_signal"


def evaluate_api_response(conversation: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    observed_cues = _observed_cues(result)
    expected_cues = set(str(cue) for cue in conversation["expected_cues"])
    missing_expected = sorted(cue for cue in expected_cues if cue not in observed_cues and conversation["category"] != "low_signal")
    unexpected_cues = sorted(cue for cue in observed_cues if cue not in expected_cues and conversation["category"] != "low_signal")
    evidence_rows = result.get("evidence", []) or []
    evidence_complete = bool(evidence_rows) and all(
        isinstance(item, dict)
        and str(item.get("evidence_text", "")).strip()
        and int(item.get("span_end", item.get("end_offset", 0)) or 0) > int(item.get("span_start", item.get("start_offset", 0)) or 0)
        for item in evidence_rows
    )
    user_facing = _safe_user_facing_text(result)
    forbidden_hits = [
        pattern for pattern in FORBIDDEN_OUTPUT_PATTERNS
        if re.search(pattern, user_facing, flags=re.IGNORECASE)
    ]
    numeric_confidence_absent = not re.search(
        r"\b\d{1,3}\s?%\b|\bconfidence\s*(?:score|percent|percentage)\b",
        user_facing,
        flags=re.IGNORECASE,
    )
    repair_text = " ".join(str(item) for item in result.get("safe_next_steps", []) or [])
    repair_text += " " + " ".join(
        str(item.get("repair_suggestion", ""))
        for item in evidence_rows
        if isinstance(item, dict)
    )
    repair_suggestion_safe = not re.search(r"\b(?:manipulate|make them|win them back|pressure them)\b", repair_text, flags=re.IGNORECASE)
    signal_strength = _signal_strength(result)
    signal_strength_valid = signal_strength in SIGNAL_STRENGTHS
    low_signal_fallback = _low_signal_fallback(result)
    expected_low_signal = conversation["expected_result_type"] == "low_signal"
    low_signal_correct = low_signal_fallback is expected_low_signal
    cannot_infer_present = isinstance(result.get("cannot_infer"), list) and bool(result.get("cannot_infer"))
    cue_contract_passed = not missing_expected and not unexpected_cues

    evaluation_errors: list[str] = []
    if missing_expected:
        evaluation_errors.append("expected_cue_missing")
    if unexpected_cues:
        evaluation_errors.append("unexpected_cue")
    if not evidence_complete and not expected_low_signal:
        evaluation_errors.append("evidence_span_missing")
    if not cannot_infer_present:
        evaluation_errors.append("cannot_infer_missing")
    if not signal_strength_valid:
        evaluation_errors.append("signal_strength_invalid")
    if forbidden_hits:
        evaluation_errors.append("unsafe_output")
    if not numeric_confidence_absent:
        evaluation_errors.append("numeric_confidence_leak")
    if not low_signal_correct:
        evaluation_errors.append("low_signal_fallback_mismatch")
    if not repair_suggestion_safe:
        evaluation_errors.append("repair_suggestion_unsafe")

    return {
        "fixture_id": conversation["fixture_id"],
        "category": conversation["category"],
        "category_scope": conversation["category_scope"],
        "source_type": "synthetic_fixture",
        "endpoint": "/api/analyze",
        "expected_result_type": conversation["expected_result_type"],
        "expected_cues": sorted(expected_cues),
        "observed_cues": sorted(observed_cues),
        "missing_expected_cues": missing_expected,
        "unexpected_cues": unexpected_cues,
        "result_state": str(result.get("result_state", "")),
        "signal_state": str(result.get("signal_state", "")),
        "signal_strength": signal_strength,
        "signal_strength_valid": signal_strength_valid,
        "evidence_row_count": len(evidence_rows),
        "evidence_complete": evidence_complete if not expected_low_signal else True,
        "cannot_infer_present": cannot_infer_present,
        "unsafe_output_hits": forbidden_hits,
        "unsafe_output_absent": not forbidden_hits,
        "numeric_confidence_absent": numeric_confidence_absent,
        "low_signal_fallback": low_signal_fallback,
        "low_signal_correct": low_signal_correct,
        "repair_suggestion_safe": repair_suggestion_safe,
        "cue_contract_passed": cue_contract_passed,
        "passed": not evaluation_errors,
        "evaluation_errors": evaluation_errors,
        "result_excerpt": {
            "safe_summary": str(result.get("safe_summary", "")),
            "signal_state": str(result.get("signal_state", "")),
            "signal_strength": signal_strength,
            "evidence_count": len(evidence_rows),
        },
    }


def evaluate_conversation_with_api(conversation: dict[str, Any], *, api_url: str, timeout: float) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = analyze_payload_for(conversation)
    try:
        result = _api_analyze(api_url, payload, timeout)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError, json.JSONDecodeError):
        safe_result = {
            "conversation_id": conversation["fixture_id"],
            "api_error": True,
            "api_error_type": "api_request_failed",
        }
        evaluation = {
            "fixture_id": conversation["fixture_id"],
            "category": conversation["category"],
            "category_scope": conversation["category_scope"],
            "source_type": "synthetic_fixture",
            "endpoint": "/api/analyze",
            "expected_result_type": conversation["expected_result_type"],
            "expected_cues": conversation["expected_cues"],
            "observed_cues": [],
            "missing_expected_cues": conversation["expected_cues"],
            "unexpected_cues": [],
            "api_error": True,
            "evaluation_errors": ["api_request_failed"],
            "passed": False,
        }
        return safe_result, evaluation
    response_record = {
        "fixture_id": conversation["fixture_id"],
        "category": conversation["category"],
        "source_type": "synthetic_fixture",
        "endpoint": "/api/analyze",
        "api_response": result,
    }
    return response_record, evaluate_api_response(conversation, result)


def _rate(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator}" if denominator else "0/0"


def build_api_regression_report(conversations: list[dict[str, Any]], selected: list[dict[str, Any]], evaluations: list[dict[str, Any]], *, api_url: str, seed: int) -> str:
    total = len(evaluations)
    passed = sum(1 for row in evaluations if row.get("passed") is True)
    cue_contract = sum(1 for row in evaluations if row.get("cue_contract_passed") is True)
    evidence_complete = sum(1 for row in evaluations if row.get("evidence_complete") is True)
    unsafe_blocked = sum(1 for row in evaluations if row.get("unsafe_output_absent") is True)
    fallback_correct = sum(1 for row in evaluations if row.get("low_signal_correct") is True)
    missing = sum(len(row.get("missing_expected_cues", [])) for row in evaluations)
    unexpected = sum(len(row.get("unexpected_cues", [])) for row in evaluations)
    api_errors = sum(1 for row in evaluations if row.get("api_error") is True)
    categories: dict[str, int] = {}
    for row in selected:
        categories[row["category"]] = categories.get(row["category"], 0) + 1
    return "\n".join(
        [
            "# Engine API Regression Report",
            "",
            "Status: synthetic API regression only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, diagnosis, or production readiness.",
            "",
            f"- API base URL: `{api_url}`",
            "- Endpoint: `/api/analyze`",
            f"- Seed: `{seed}`",
            f"- Synthetic fixture pool: `{len(conversations)}` conversations / `{sum(int(row['message_count']) for row in conversations)}` messages",
            f"- Evaluated synthetic conversations: `{total}`",
            f"- API regression pass rate: `{_rate(passed, total)}`",
            f"- Cue contract pass rate: `{_rate(cue_contract, total)}`",
            f"- Evidence completeness rate: `{_rate(evidence_complete, total)}`",
            f"- Unsafe-output block rate: `{_rate(unsafe_blocked, total)}`",
            f"- Fallback correctness rate: `{_rate(fallback_correct, total)}`",
            f"- API transport failures: `{api_errors}`",
            f"- Missing expected cue count: `{missing}`",
            f"- Unexpected cue count: `{unexpected}`",
            "",
            "## Evaluated Conversation Counts",
            "",
            *[f"- `{category}`: `{count}`" for category, count in sorted(categories.items())],
            "",
            "## Notes",
            "",
            "- `/api/analyze` returns deterministic cue evidence, not the full match result. Match-specific expected cues may appear as false negatives until the analyze route exposes equivalent evidence.",
            "- `cheating_ambiguous` is private synthetic evaluation metadata only and must never be described as product capability.",
            "- Reports store synthetic API responses separately from fixture definitions under `reports/engine_eval/`.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic WhatsApp fixtures and optionally run API regression against /api/analyze.")
    parser.add_argument("--messages", type=int, default=1000)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--engine-report-dir", default=str(DEFAULT_ENGINE_REPORT_DIR))
    parser.add_argument("--api-url", default=os.environ.get("VIBE_SIGNAL_API_URL", ""))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--no-api", action="store_true", help="Generate fixture definitions only; do not evaluate locally or call an API.")
    args = parser.parse_args(argv)

    conversations = build_conversations(args.messages, seed=args.seed)
    out_dir = Path(args.out_dir)
    write_jsonl(out_dir / "conversations.jsonl", conversations)

    if args.no_api:
        print(
            json.dumps(
                {
                    "status": "fixtures_only",
                    "messages": sum(int(row["message_count"]) for row in conversations),
                    "conversations": len(conversations),
                    "out_dir": str(out_dir),
                    "api_evaluated": False,
                    "seed": int(args.seed),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    api_url = normalize_api_url(args.api_url)
    selected = select_for_api_regression(conversations, limit=args.limit, seed=args.seed)
    response_rows: list[dict[str, Any]] = []
    evaluation_rows: list[dict[str, Any]] = []
    for conversation in selected:
        response_record, evaluation = evaluate_conversation_with_api(conversation, api_url=api_url, timeout=float(args.timeout))
        response_rows.append(response_record)
        evaluation_rows.append(evaluation)

    report_dir = Path(args.engine_report_dir)
    write_jsonl(report_dir / "api_responses.jsonl", response_rows)
    write_jsonl(report_dir / "api_regression_results.jsonl", evaluation_rows)
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "api_regression_report.md").write_text(
        build_api_regression_report(conversations, selected, evaluation_rows, api_url=api_url, seed=int(args.seed)),
        encoding="utf-8",
    )
    api_errors = sum(1 for row in evaluation_rows if row.get("api_error") is True)
    print(
        json.dumps(
            {
                "status": "api_regression_complete" if api_errors == 0 else "api_regression_transport_failed",
                "messages": sum(int(row["message_count"]) for row in conversations),
                "conversations": len(conversations),
                "evaluated_conversations": len(evaluation_rows),
                "passed_evaluations": sum(1 for row in evaluation_rows if row.get("passed") is True),
                "api_errors": api_errors,
                "out_dir": str(out_dir),
                "engine_report_dir": str(report_dir),
                "seed": int(args.seed),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if api_errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
