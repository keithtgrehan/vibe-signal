#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.validate_synthetic_whatsapp_training_rows import (  # noqa: E402
    ALLOWED_CUES,
    BLOCKED_INTERPRETATIONS,
    BLOCKED_LABELS,
    FORBIDDEN_OUTPUTS,
    FORBIDDEN_PUBLIC_CLAIM_PATTERNS,
    CONSENT_STATUS,
    RIGHTS_REVIEW_STATUS,
    SOURCE_TIER,
    SOURCE_TYPE,
    validate_rows,
)


DEFAULT_INPUT_DIR = REPO_ROOT / "data" / "synthetic" / "whatsapp"
DEFAULT_OUT = REPO_ROOT / "data" / "training" / "pattern_recognition" / "synthetic_whatsapp_10k_training_rows.jsonl"
DEFAULT_MANIFEST_OUT = REPO_ROOT / "data" / "training" / "pattern_recognition" / "synthetic_whatsapp_10k_manifest.json"
DEFAULT_REPORT_OUT = REPO_ROOT / "reports" / "pattern_training" / "synthetic_whatsapp_10k_training_rows_report.md"

SAFE_NEXT_STEP = "Clarify one concrete point, slow down, set a boundary, re-ask directly, or pause before replying."
NON_CLAIMS = (
    "Synthetic-only fixture conversion; not real-world accuracy, model quality, production readiness, "
    "legal/compliance approval, or evidence that Vibe Signal can infer private motives or outcomes."
)

CUE_SPAN_PATTERNS: dict[str, tuple[str, ...]] = {
    "directness": (r"\b(?:can you|could you|will you|would you|did you|do you|are we|are you|confirm|send|review|answer)\b[^.!?\n]*[.!?]?",),
    "specificity": (r"\b(?:friday|saturday|sunday|monday|tuesday|wednesday|thursday|today|tonight|tomorrow|lunch|dinner|noon|\d{1,2}(?::\d{2})?\s?(?:am|pm)?)\b[^.!?\n]*[.!?]?",),
    "specificity_drop": (r"\b(?:maybe later|sometime|not sure yet|actually, maybe)\b[^.!?\n]*[.!?]?",),
    "ambiguity": (r"\b(?:maybe|not sure|whatever|sometime|unclear|i guess|we'll see|later)\b[^.!?\n]*[.!?]?",),
    "unclear_ask": (r"\b(?:that thing|soon maybe|deal with that|which thing)\b[^.!?\n]*[.!?]?",),
    "hedging": (r"\b(?:maybe|perhaps|i guess|i think|not sure|might|could be)\b[^.!?\n]*[.!?]?",),
    "reassurance": (r"\b(?:no rush|no pressure|no stress|all good|no worries|if you have space|when you can)\b[^.!?\n]*[.!?]?",),
    "alignment": (r"\b(?:that works|sounds good|same page|yes|thanks for resetting)\b[^.!?\n]*[.!?]?",),
    "pressure": (r"\b(?:you have to|right now|you must|why won't you|don't say no|owe me)\b[^.!?\n]*[.!?]?",),
    "urgency": (r"\b(?:right now|urgent|asap|deadline|by \d{1,2}(?::\d{2})?\s?(?:am|pm)?|by tonight|today)\b[^.!?\n]*[.!?]?",),
    "boundary_pressure": (r"\b(?:share my location|send me your location|send me your|why won't you|you have to explain|prove it)\b[^.!?\n]*[.!?]?",),
    "consent_clarity": (r"\b(?:you can say no|only if you want|no pressure)\b[^.!?\n]*[.!?]?",),
    "conflict": (r"\b(?:frustrated|upset|not okay|fight|argument|tense|hurt)\b[^.!?\n]*[.!?]*",),
    "escalation_risk": (r"\b(?:!!|right now|you have to|keeps happening)\b[^.!?\n]*[.!?]*",),
    "repair_opportunity": (r"\b(?:sorry|let me rephrase|reset|repair|thanks for resetting|i meant)\b[^.!?\n]*[.!?]?",),
    "topic_shift": (r"\b(?:anyway|separately|another thing|new topic|switching topics)\b[^.!?\n]*[.!?]?",),
    "answer_evasion_pattern": (r"\b(?:anyway|separately|maybe later|did you finish|the meeting moved)\b[^.!?\n]*[.!?]?",),
    "cognitive_load": (r".{80,}",),
    "overloaded_message": (r".{80,}",),
    "contradiction_against_prior_message": (r"\b(?:i already sent|i have not sent|i will send|i cannot send|friday at 7pm)\b[^.!?\n]*[.!?]?",),
    "unsupported_claim_shift": (r"\b(?:approved|not approved|after all)\b[^.!?\n]*[.!?]?",),
}

UNSAFE_SCENARIO_REPLACEMENTS = (
    (re.compile(r"cheating", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"lying", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"diagnosis", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"attachment_style", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"hidden_intent", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"manipulation", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"therapy_advice", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"do_they_like_me", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"make_them_reply", re.IGNORECASE), "blocked_claim"),
    (re.compile(r"private_eval_label", re.IGNORECASE), "synthetic_eval_label"),
)


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def discover_fixture_files(input_dir: Path) -> tuple[Path, list[Path]]:
    combined = input_dir / "conversations.jsonl"
    split_files = sorted(path for path in input_dir.glob("*/conversations.jsonl") if path.is_file())
    if combined.exists():
        return combined, split_files
    if split_files:
        return split_files[0], split_files
    raise FileNotFoundError(f"no conversations.jsonl fixtures found under {input_dir}")


def _safe_scenario_family(value: Any) -> str:
    scenario = str(value or "unknown").strip().lower().replace(" ", "_") or "unknown"
    for pattern, replacement in UNSAFE_SCENARIO_REPLACEMENTS:
        scenario = pattern.sub(replacement, scenario)
    scenario = re.sub(r"[^a-z0-9_:-]+", "_", scenario)
    if scenario.startswith("user_asks_"):
        scenario = "red_team_blocked_claim_prompt"
    return scenario[:80] or "unknown"


def _normalize_speaker(value: Any) -> str:
    speaker = str(value or "").strip().lower()
    if speaker in {"self", "me", "mine"}:
        return "self"
    if speaker in {"other", "them", "they"}:
        return "other"
    return "unknown"


def _source_is_synthetic(row: dict[str, Any]) -> bool:
    if row.get("synthetic") is not True:
        return False
    if row.get("source_type") != SOURCE_TYPE:
        return False
    if row.get("not_copied_from_real_chat") is not True:
        return False
    messages = row.get("messages")
    return isinstance(messages, list) and all(isinstance(message, dict) and message.get("synthetic") is True for message in messages)


def _unsafe_output_text(value: str) -> bool:
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in FORBIDDEN_PUBLIC_CLAIM_PATTERNS.values())


def _extract_messages(row: dict[str, Any]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for index, message in enumerate(row.get("messages", []), start=1):
        if not isinstance(message, dict):
            raise ValueError(f"{row.get('conversation_id')}: message {index} is not an object")
        text = str(message.get("text", "")).strip()
        if not text:
            continue
        speaker = _normalize_speaker(message.get("speaker") or message.get("author"))
        messages.append(
            {
                "message_id": str(message.get("message_id") or message.get("id") or f"m{index}"),
                "speaker_role": speaker,
                "text": text,
            }
        )
    if not messages:
        raise ValueError(f"{row.get('conversation_id')}: no non-empty messages")
    return messages


def _text_for_training(messages: list[dict[str, str]]) -> str:
    return "\n".join(f"{message['speaker_role']}: {message['text']}" for message in messages)


def _extract_expected_cues(row: dict[str, Any], excluded_counter: Counter[str]) -> list[str]:
    expected: list[str] = []
    for cue in row.get("expected_cues", []) if isinstance(row.get("expected_cues"), list) else []:
        cue_text = str(cue).strip()
        if not cue_text:
            continue
        if cue_text in BLOCKED_LABELS:
            raise ValueError(f"{row.get('conversation_id')}: blocked expected cue {cue_text}")
        if cue_text not in ALLOWED_CUES:
            excluded_counter[cue_text] += 1
            continue
        if cue_text not in expected:
            expected.append(cue_text)
    if not expected:
        strength = str(row.get("expected_signal_strength", "")).strip().lower()
        scenario = str(row.get("scenario") or row.get("category") or "").strip().lower()
        expected.append("low_signal" if strength == "insufficient" or "low_signal" in scenario else "neutral")
    return expected


def _first_short_message(text_for_training: str) -> str:
    for line in text_for_training.splitlines():
        _, _, text = line.partition(": ")
        candidate = text.strip()
        if candidate:
            return candidate[:120]
    return text_for_training[:120]


def _span_for_cue(cue: str, text_for_training: str) -> str:
    for pattern in CUE_SPAN_PATTERNS.get(cue, ()):
        match = re.search(pattern, text_for_training, flags=re.IGNORECASE | re.DOTALL)
        if match:
            span = match.group(0).strip()
            if span:
                return span[:160]
    return _first_short_message(text_for_training)


def _evidence_explanation(cue: str) -> str:
    cue_readable = cue.replace("_", " ")
    return f"The span is an observable synthetic phrase associated with the {cue_readable} cue."


def _build_evidence_spans(expected_cues: list[str], text_for_training: str) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    for cue in expected_cues:
        if cue in {"low_signal", "neutral"}:
            continue
        evidence.append({"cue_type": cue, "span": _span_for_cue(cue, text_for_training), "explanation": _evidence_explanation(cue)})
    return evidence


def _safe_summary(expected_cues: list[str]) -> str:
    if "low_signal" in expected_cues:
        return "The synthetic exchange is short or low-context, so only limited wording patterns can be reviewed."
    if "neutral" in expected_cues:
        return "The synthetic exchange is cue-light and does not need a strong pattern label."
    cue_list = ", ".join(cue.replace("_", " ") for cue in expected_cues[:4])
    suffix = " and related wording cues" if len(expected_cues) > 4 else ""
    return f"The synthetic exchange contains observable {cue_list}{suffix}."


def convert_fixture_row(row: dict[str, Any], index: int, excluded_counter: Counter[str]) -> dict[str, Any]:
    if not _source_is_synthetic(row):
        raise ValueError(f"{row.get('conversation_id') or index}: row is missing required synthetic provenance")
    messages = _extract_messages(row)
    text_for_training = _text_for_training(messages)
    expected_cues = _extract_expected_cues(row, excluded_counter)
    safe_summary = _safe_summary(expected_cues)
    safe_next_step = SAFE_NEXT_STEP
    if _unsafe_output_text(safe_summary) or _unsafe_output_text(safe_next_step):
        raise ValueError(f"{row.get('conversation_id')}: generated safe output contains a forbidden claim")

    return {
        "row_id": f"synthetic_whatsapp_{index:06d}",
        "conversation_id": str(row.get("conversation_id") or row.get("fixture_id") or f"synthetic_whatsapp_{index:06d}"),
        "source_tier": SOURCE_TIER,
        "source_type": SOURCE_TYPE,
        "rights_review_status": RIGHTS_REVIEW_STATUS,
        "consent_status": CONSENT_STATUS,
        "commercial_training_allowed": False,
        "research_training_allowed": True,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "contains_raw_private_text": False,
        "contains_personal_data": False,
        "redaction_status": "synthetic",
        "review_status": "synthetic_expected",
        "split": str(row.get("split") or "unknown"),
        "scenario_family": _safe_scenario_family(row.get("scenario") or row.get("category")),
        "synthetic": True,
        "not_copied_from_real_chat": True,
        "messages": messages,
        "text_for_training": text_for_training,
        "expected_cues": expected_cues,
        "evidence_spans": _build_evidence_spans(expected_cues, text_for_training),
        "blocked_interpretations": list(BLOCKED_INTERPRETATIONS),
        "forbidden_outputs": list(FORBIDDEN_OUTPUTS),
        "safe_summary": safe_summary,
        "safe_next_step": safe_next_step,
    }


def build_training_rows(source_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Counter[str]]:
    excluded_counter: Counter[str] = Counter()
    rows = [convert_fixture_row(row, index, excluded_counter) for index, row in enumerate(source_rows, start=1)]
    return rows, excluded_counter


def _load_source_manifest(input_dir: Path) -> dict[str, Any]:
    path = input_dir / "fixture_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _build_manifest(
    *,
    input_dir: Path,
    source_file: Path,
    split_files: list[Path],
    source_manifest: dict[str, Any],
    rows: list[dict[str, Any]],
    excluded_counter: Counter[str],
) -> dict[str, Any]:
    split_counts: Counter[str] = Counter(str(row["split"]) for row in rows)
    cue_counts: Counter[str] = Counter(cue for row in rows for cue in row["expected_cues"])
    scenario_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        scenario_counts[str(row["split"])][str(row["scenario_family"])] += 1
    message_count = sum(len(row["messages"]) for row in rows)
    return {
        "status": "synthetic_whatsapp_pattern_training_rows_built",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_tier": SOURCE_TIER,
        "source_type": SOURCE_TYPE,
        "rights_review_status": RIGHTS_REVIEW_STATUS,
        "consent_status": CONSENT_STATUS,
        "synthetic": True,
        "research_training_allowed": True,
        "commercial_training_allowed": False,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "contains_raw_private_text": False,
        "contains_personal_data": False,
        "input_dir": str(input_dir),
        "source_file": str(source_file),
        "discovered_split_files": [str(path) for path in split_files],
        "source_manifest_path": str(input_dir / "fixture_manifest.json"),
        "source_manifest_total_messages": source_manifest.get("total_messages"),
        "source_manifest_total_conversations": source_manifest.get("total_conversations"),
        "row_count": len(rows),
        "message_count": message_count,
        "split_counts": dict(sorted(split_counts.items())),
        "cue_counts": dict(sorted(cue_counts.items())),
        "scenario_counts_by_split": {split: dict(sorted(counter.items())) for split, counter in sorted(scenario_counts.items())},
        "excluded_unsupported_cue_counts": dict(sorted(excluded_counter.items())),
        "blocked_labels": sorted(BLOCKED_LABELS),
        "allowed_labels": sorted(ALLOWED_CUES),
        "non_claims": [NON_CLAIMS],
        "deterministic_engine_remains_primary": True,
    }


def _build_report(manifest: dict[str, Any]) -> str:
    split_lines = "\n".join(f"- {split}: {count}" for split, count in manifest["split_counts"].items())
    cue_lines = "\n".join(f"- {cue}: {count}" for cue, count in manifest["cue_counts"].items())
    excluded_lines = "\n".join(
        f"- {cue}: {count}" for cue, count in manifest["excluded_unsupported_cue_counts"].items()
    ) or "- None"
    return f"""# Synthetic WhatsApp 10k Training Rows Report

Synthetic-only fixture conversion for a research-only pattern-recognition baseline.

## Source Discovery

- Input directory: `{manifest['input_dir']}`
- Source JSONL: `{manifest['source_file']}`
- Source manifest: `{manifest['source_manifest_path']}`
- Discovered source conversations: `{manifest.get('source_manifest_total_conversations')}`
- Discovered source messages: `{manifest.get('source_manifest_total_messages')}`
- Training rows written: `{manifest['row_count']}`
- Synthetic messages represented: `{manifest['message_count']}`

## Split Counts

{split_lines}

## Cue Counts

{cue_lines}

## Unsupported Fixture Cues Excluded From Training Labels

{excluded_lines}

## Safety Boundary

{NON_CLAIMS}

The deterministic cue engine remains primary. This model-training row set is for local research-only cue-family baseline work. Model output must not be rendered directly in the product UI. Future model-assisted output would need evidence-span validation, safe-output blocking, blocked-claim sanitization, low-signal fallback handling, and a human-reviewed evaluation gate.

No human data, semi-synthetic data, private chats, tester messages, provider outputs, external datasets, screenshots, embeddings, vectors, checkpoints, or model artifacts are included.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build research-only pattern training rows from synthetic WhatsApp fixtures.")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--manifest-out", default=str(DEFAULT_MANIFEST_OUT))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT_OUT))
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    try:
        source_file, split_files = discover_fixture_files(input_dir)
        source_rows = read_jsonl(source_file)
        rows, excluded_counter = build_training_rows(source_rows)
        source_manifest = _load_source_manifest(input_dir)
        manifest = _build_manifest(
            input_dir=input_dir,
            source_file=source_file,
            split_files=split_files,
            source_manifest=source_manifest,
            rows=rows,
            excluded_counter=excluded_counter,
        )
        validation_errors, _summary = validate_rows(rows, manifest)
        if validation_errors:
            raise ValueError("generated rows failed validation: " + "; ".join(validation_errors[:20]))
        write_jsonl(Path(args.out), rows)
        _write_json(Path(args.manifest_out), manifest)
        report_path = Path(args.report_out)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(_build_report(manifest), encoding="utf-8")
    except Exception as exc:
        print(f"Synthetic WhatsApp training-row conversion failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "built",
                "rows": len(rows),
                "messages": manifest["message_count"],
                "out": str(Path(args.out)),
                "manifest_out": str(Path(args.manifest_out)),
                "report_out": str(Path(args.report_out)),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
