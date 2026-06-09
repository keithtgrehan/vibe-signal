#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
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
    MANIPULATION_NEXT_STEP_PATTERNS,
)


GOEMOTIONS_SOURCE_TIER = "goemotions_local_research_apache2"
MELD_SOURCE_TIER = "meld_local_research_gpl3_nc"
LOCAL_SOURCE_TIERS = {GOEMOTIONS_SOURCE_TIER, MELD_SOURCE_TIER}
LOCAL_SOURCE_TYPES = {
    GOEMOTIONS_SOURCE_TIER: "external_public_dataset_local_cache",
    MELD_SOURCE_TIER: "external_transcript_dataset_local_cache",
}
LOCAL_RIGHTS_STATUS = {
    GOEMOTIONS_SOURCE_TIER: "apache_2_0_metadata_confirmed",
    MELD_SOURCE_TIER: "gpl_3_0_local_noncommercial_research_only",
}
LOCAL_CONSENT_STATUS = {
    GOEMOTIONS_SOURCE_TIER: "public_dataset_local_research",
    MELD_SOURCE_TIER: "public_transcript_dataset_local_research",
}

NON_CLAIMS = (
    "Synthetic and local public-dataset metrics are development signals only. They are not real-world "
    "validation, model-quality proof, production-readiness proof, legal/compliance approval, or a claim "
    "that Vibe Signal can infer hidden intent, attraction, deception, diagnosis, manipulation, abuse, "
    "or relationship outcomes."
)

DETERMINISTIC_ENGINE_BOUNDARY = (
    "The deterministic cue engine remains primary. This model is a research-only cue-family baseline; "
    "model output must not be rendered directly in product UI."
)

FUTURE_MODEL_GATE = (
    "Future model-assisted output must pass evidence-span validation, the safe-output blocker, "
    "blocked-claim sanitizer, low-signal fallback, and a human-reviewed evaluation gate."
)

GOEMOTIONS_LABELS = {
    0: "admiration",
    1: "amusement",
    2: "anger",
    3: "annoyance",
    4: "approval",
    5: "caring",
    6: "confusion",
    7: "curiosity",
    8: "desire",
    9: "disappointment",
    10: "disapproval",
    11: "disgust",
    12: "embarrassment",
    13: "excitement",
    14: "fear",
    15: "gratitude",
    16: "grief",
    17: "joy",
    18: "love",
    19: "nervousness",
    20: "optimism",
    21: "pride",
    22: "realization",
    23: "relief",
    24: "remorse",
    25: "sadness",
    26: "surprise",
    27: "neutral",
}

MELD_EMOTIONS = {"neutral", "joy", "sadness", "anger", "surprise", "fear", "disgust"}
MELD_SENTIMENTS = {"positive", "neutral", "negative"}

LOCAL_ROW_REQUIRED_FIELDS = {
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
    "contains_private_or_tester_text",
    "contains_public_dataset_text",
    "contains_personal_data_risk",
    "row_commit_allowed",
    "aggregate_report_only",
    "redaction_status",
    "review_status",
    "split",
    "scenario_family",
    "messages",
    "text_for_training",
    "expected_cues",
    "evidence_spans",
    "source_labels",
    "blocked_interpretations",
    "forbidden_outputs",
    "safe_summary",
    "safe_next_step",
}

UNSAFE_PUBLIC_REPORT_PHRASES = (
    "accurate",
    "validated",
    "production-grade",
    "hidden intent detection",
    "attraction prediction",
    "deception detection",
    "diagnosis detection",
    "manipulation detection",
    "relationship outcome prediction",
)

QUESTION_RE = re.compile(r"\?")
CUE_PATTERNS: dict[str, tuple[str, ...]] = {
    "directness": (
        r"\b(?:can you|could you|will you|would you|please|confirm|send|review|answer|what is|what are|how do|why did)\b",
    ),
    "specificity": (
        r"\b(?:today|tonight|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|noon|midnight|\d{1,2}(?::\d{2})?\s?(?:am|pm))\b",
    ),
    "ambiguity": (
        r"\b(?:maybe|perhaps|not sure|i guess|i wonder|unclear|whatever|could be|might be|we'll see|hard to tell)\b",
    ),
    "unclear_ask": (
        r"\b(?:what do you mean|what is going on|i don't know|i dont know|not sure what|can someone explain)\b",
    ),
    "hedging": (
        r"\b(?:maybe|perhaps|i guess|i think|might|could|probably|sort of|kind of|not sure)\b",
    ),
    "reassurance": (
        r"\b(?:no worries|no pressure|it's okay|it is okay|all good|happy to help|you can take your time|thanks|thank you|appreciate)\b",
    ),
    "alignment": (
        r"\b(?:i agree|agreed|sounds good|that works|yes|true|same page|good point|makes sense|approved)\b",
    ),
    "pressure": (
        r"\b(?:you have to|you must|right now|owe me|do it now|don't say no|dont say no|make sure you)\b",
    ),
    "urgency": (
        r"\b(?:urgent|asap|right now|immediately|deadline|need this now|before it is too late)\b",
    ),
    "boundary_pressure": (
        r"\b(?:send me your|share your|prove it|why won't you|why wont you|don't tell anyone|dont tell anyone|your location)\b",
    ),
    "consent_clarity": (
        r"\b(?:you can say no|only if you want|is that okay|are you okay with|we can stop|stop anytime)\b",
    ),
    "conflict": (
        r"\b(?:angry|annoyed|upset|frustrated|not okay|disagree|argument|fight|ridiculous|stupid|wrong|hurt)\b",
    ),
    "escalation_risk": (
        r"(?:!!|\b(?:right now|you have to|you must|this is not okay|stop ignoring)\b)",
    ),
    "repair_opportunity": (
        r"\b(?:sorry|apologies|forgive|my fault|i take it back|let me rephrase|i meant|reset)\b",
    ),
    "topic_shift": (
        r"\b(?:anyway|separately|new topic|switching topics|another thing)\b",
    ),
    "answer_evasion_pattern": (
        r"\b(?:anyway|separately|that's not the point|that is not the point|let's not talk about)\b",
    ),
}

GOEMOTIONS_LABEL_TO_CUES: dict[str, tuple[str, ...]] = {
    "neutral": ("neutral",),
    "confusion": ("ambiguity", "unclear_ask"),
    "curiosity": ("directness", "unclear_ask"),
    "approval": ("alignment",),
    "gratitude": ("reassurance", "alignment"),
    "caring": ("reassurance",),
    "relief": ("reassurance",),
    "optimism": ("reassurance", "alignment"),
    "anger": ("conflict", "escalation_risk"),
    "annoyance": ("conflict",),
    "disapproval": ("conflict",),
    "disgust": ("conflict",),
    "remorse": ("repair_opportunity",),
}

MELD_LABEL_TO_CUES: dict[str, tuple[str, ...]] = {
    "neutral": ("neutral",),
    "positive": ("alignment", "reassurance"),
    "negative": ("conflict",),
    "anger": ("conflict", "escalation_risk"),
    "disgust": ("conflict",),
    "joy": ("alignment", "reassurance"),
}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
                raise ValueError(f"{path}:{line_number}: JSONL row must be an object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_local_row_output_path(path: Path) -> None:
    """External public dataset rows must stay in ignored local-only locations."""
    resolved = path.expanduser().resolve()
    allowed_roots = [
        (REPO_ROOT / "data" / "external").resolve(),
        (Path.cwd() / ".local_artifacts").resolve(),
    ]
    for root in allowed_roots:
        try:
            resolved.relative_to(root)
            return
        except ValueError:
            continue
    raise ValueError("local external row output must be under data/external/ or .local_artifacts/")


def normalize_split(value: str) -> str:
    split = str(value or "unknown").strip().lower()
    aliases = {"val": "validation", "dev": "validation"}
    return aliases.get(split, split or "unknown")


def normalize_label(value: Any, label_names: dict[int, str] | None = None) -> str:
    if isinstance(value, int):
        if label_names is None:
            label_names = GOEMOTIONS_LABELS
        return label_names.get(value, str(value)).strip().lower()
    text = str(value or "").strip().lower().replace(" ", "_")
    if text.isdigit():
        return normalize_label(int(text), label_names)
    return text


def label_indices_to_names(values: Any, label_names: dict[int, str] | None = None) -> list[str]:
    if label_names is None:
        label_names = GOEMOTIONS_LABELS
    if isinstance(values, str):
        try:
            parsed = json.loads(values)
            values = parsed
        except json.JSONDecodeError:
            values = [part.strip() for part in values.split(",") if part.strip()]
    if not isinstance(values, list):
        values = [values]
    labels: list[str] = []
    for value in values:
        label = normalize_label(value, label_names)
        if label and label not in labels:
            labels.append(label)
    return labels


def _pattern_span(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return ""
    return match.group(0).strip()[:160]


def detect_text_cues(text: str) -> dict[str, str]:
    cue_to_span: dict[str, str] = {}
    for cue, patterns in CUE_PATTERNS.items():
        for pattern in patterns:
            span = _pattern_span(text, pattern)
            if span:
                cue_to_span[cue] = span
                break
    if QUESTION_RE.search(text) and "directness" not in cue_to_span:
        cue_to_span["unclear_ask"] = text.strip()[:160]
    word_count = len(re.findall(r"\w+", text))
    question_count = len(QUESTION_RE.findall(text))
    if word_count >= 45 or question_count >= 3:
        cue_to_span.setdefault("cognitive_load", text.strip()[:220])
        cue_to_span.setdefault("overloaded_message", text.strip()[:220])
    if {"pressure", "conflict"} <= set(cue_to_span) or {"pressure", "boundary_pressure"} <= set(cue_to_span):
        cue_to_span.setdefault("escalation_risk", text.strip()[:220])
    return cue_to_span


def cues_from_goemotions(text: str, labels: list[str]) -> tuple[list[str], list[dict[str, str]]]:
    return _cues_from_external_labels(text, labels, GOEMOTIONS_LABEL_TO_CUES)


def cues_from_meld(text: str, labels: list[str]) -> tuple[list[str], list[dict[str, str]]]:
    return _cues_from_external_labels(text, labels, MELD_LABEL_TO_CUES)


def _cues_from_external_labels(
    text: str,
    labels: list[str],
    label_to_cues: dict[str, tuple[str, ...]],
) -> tuple[list[str], list[dict[str, str]]]:
    text_spans = detect_text_cues(text)
    expected: list[str] = []
    evidence: list[dict[str, str]] = []
    label_candidates: set[str] = set()
    for label in labels:
        label_candidates.update(label_to_cues.get(label, ()))

    for cue in sorted(label_candidates):
        if cue in {"neutral", "low_signal"}:
            continue
        span = text_spans.get(cue)
        if not span:
            continue
        expected.append(cue)
        evidence.append(
            {
                "cue_type": cue,
                "span": span,
                "explanation": f"Local weak-label mapping found observable wording for the {cue.replace('_', ' ')} cue.",
            }
        )

    for cue, span in sorted(text_spans.items()):
        if cue not in expected and cue in ALLOWED_CUES:
            expected.append(cue)
            evidence.append(
                {
                    "cue_type": cue,
                    "span": span,
                    "explanation": f"Observable text pattern matched the {cue.replace('_', ' ')} cue.",
                }
            )

    if not expected:
        if "neutral" in label_candidates or "neutral" in labels:
            expected.append("neutral")
        else:
            expected.append("low_signal")
    return expected, evidence


def safe_summary_for(cues: list[str], source_name: str) -> str:
    cue_text = ", ".join(cue.replace("_", " ") for cue in cues if cue not in {"neutral", "low_signal"})
    if cue_text:
        return f"The local {source_name} row contains observable wording cues: {cue_text}."
    return f"The local {source_name} row has low signal for Vibe communication-pattern cues."


def build_local_research_row(
    *,
    source_tier: str,
    row_number: int,
    source_row_id: str,
    split: str,
    text: str,
    labels: list[str],
    expected_cues: list[str],
    evidence_spans: list[dict[str, str]],
) -> dict[str, Any]:
    if source_tier not in LOCAL_SOURCE_TIERS:
        raise ValueError(f"unsupported local source_tier {source_tier!r}")
    clean_text = str(text or "").strip()
    if not clean_text:
        raise ValueError("local research row text cannot be empty")
    prefix = "goemotions" if source_tier == GOEMOTIONS_SOURCE_TIER else "meld"
    source_suffix = str(source_row_id or f"{row_number:06d}").strip()
    source_suffix = re.sub(r"[^a-zA-Z0-9_.:-]+", "_", source_suffix)[:80] or f"{row_number:06d}"
    return {
        "row_id": f"{prefix}_local_research_{row_number:06d}",
        "conversation_id": f"{prefix}_{source_suffix}",
        "source_tier": source_tier,
        "source_type": LOCAL_SOURCE_TYPES[source_tier],
        "rights_review_status": LOCAL_RIGHTS_STATUS[source_tier],
        "consent_status": LOCAL_CONSENT_STATUS[source_tier],
        "commercial_training_allowed": False,
        "research_training_allowed": True,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "contains_raw_private_text": False,
        "contains_private_or_tester_text": False,
        "contains_public_dataset_text": True,
        "contains_personal_data_risk": True,
        "row_commit_allowed": False,
        "aggregate_report_only": True,
        "redaction_status": "local_public_dataset_only",
        "review_status": "weak_label_candidate",
        "split": normalize_split(split),
        "scenario_family": f"{prefix}_weak_label_mapping",
        "messages": [{"message_id": "m1", "speaker_role": "unknown", "text": clean_text}],
        "text_for_training": f"unknown: {clean_text}",
        "expected_cues": expected_cues,
        "evidence_spans": evidence_spans,
        "source_labels": labels,
        "blocked_interpretations": BLOCKED_INTERPRETATIONS,
        "forbidden_outputs": FORBIDDEN_OUTPUTS,
        "safe_summary": safe_summary_for(expected_cues, prefix),
        "safe_next_step": "Use this as a local research cue candidate only; verify observable spans before any product use.",
    }


def _contains_pattern(text: str, patterns: dict[str, str]) -> list[str]:
    return [name for name, pattern in patterns.items() if re.search(pattern, text, flags=re.IGNORECASE)]


def validate_local_research_row(row: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    missing = sorted(LOCAL_ROW_REQUIRED_FIELDS - set(row))
    if missing:
        return [f"row {index}: missing required fields: {', '.join(missing)}"]

    source_tier = str(row.get("source_tier", ""))
    if source_tier not in LOCAL_SOURCE_TIERS:
        errors.append(f"row {index}: unsupported source_tier {source_tier!r}")
    else:
        if row.get("source_type") != LOCAL_SOURCE_TYPES[source_tier]:
            errors.append(f"row {index}: source_type does not match {source_tier}")
        if row.get("rights_review_status") != LOCAL_RIGHTS_STATUS[source_tier]:
            errors.append(f"row {index}: rights_review_status does not match {source_tier}")
        if row.get("consent_status") != LOCAL_CONSENT_STATUS[source_tier]:
            errors.append(f"row {index}: consent_status does not match {source_tier}")

    required_booleans = {
        "commercial_training_allowed": False,
        "research_training_allowed": True,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "contains_raw_private_text": False,
        "contains_private_or_tester_text": False,
        "contains_public_dataset_text": True,
        "contains_personal_data_risk": True,
        "row_commit_allowed": False,
        "aggregate_report_only": True,
    }
    for field, expected in required_booleans.items():
        if row.get(field) is not expected:
            errors.append(f"row {index}: {field} must be {expected}")

    if row.get("redaction_status") != "local_public_dataset_only":
        errors.append(f"row {index}: redaction_status must be local_public_dataset_only")
    if row.get("review_status") != "weak_label_candidate":
        errors.append(f"row {index}: review_status must be weak_label_candidate")

    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) != 1:
        errors.append(f"row {index}: messages must contain exactly one local utterance")
    else:
        message = messages[0]
        if not isinstance(message, dict):
            errors.append(f"row {index}: message must be an object")
        else:
            if message.get("speaker_role") != "unknown":
                errors.append(f"row {index}: local public dataset speaker_role must be unknown")
            if not str(message.get("text", "")).strip():
                errors.append(f"row {index}: message text cannot be empty")

    text_for_training = str(row.get("text_for_training", ""))
    if not text_for_training.startswith("unknown: ") or len(text_for_training.strip()) <= len("unknown: "):
        errors.append(f"row {index}: text_for_training must use unknown speaker prefix and non-empty text")

    cues = row.get("expected_cues")
    if not isinstance(cues, list) or not all(isinstance(cue, str) and cue for cue in cues):
        errors.append(f"row {index}: expected_cues must be a non-empty list of strings")
        cues = []
    for cue in cues:
        if cue in BLOCKED_LABELS:
            errors.append(f"row {index}: blocked label in expected_cues: {cue}")
        if cue not in ALLOWED_CUES:
            errors.append(f"row {index}: unsupported cue in expected_cues: {cue}")

    evidence_spans = row.get("evidence_spans")
    if not isinstance(evidence_spans, list):
        errors.append(f"row {index}: evidence_spans must be a list")
        evidence_spans = []
    cue_set = set(cues)
    if cue_set - {"neutral", "low_signal"} and not evidence_spans:
        errors.append(f"row {index}: cue-positive local rows require evidence spans")
    evidence_cues = set()
    for evidence_index, evidence in enumerate(evidence_spans, start=1):
        if not isinstance(evidence, dict):
            errors.append(f"row {index}: evidence span {evidence_index} must be an object")
            continue
        cue_type = str(evidence.get("cue_type", ""))
        span = str(evidence.get("span", ""))
        if cue_type not in cue_set:
            errors.append(f"row {index}: evidence span {evidence_index} cue_type not in expected_cues")
        if not span.strip():
            errors.append(f"row {index}: evidence span {evidence_index} missing span")
        elif span not in text_for_training:
            errors.append(f"row {index}: evidence span {evidence_index} does not appear in text_for_training")
        if not str(evidence.get("explanation", "")).strip():
            errors.append(f"row {index}: evidence span {evidence_index} missing explanation")
        evidence_cues.add(cue_type)
    for cue in cue_set - {"neutral", "low_signal"}:
        if cue not in evidence_cues:
            errors.append(f"row {index}: missing evidence span for cue {cue}")

    if set(BLOCKED_INTERPRETATIONS) - set(row.get("blocked_interpretations", []) if isinstance(row.get("blocked_interpretations"), list) else []):
        errors.append(f"row {index}: blocked_interpretations missing required registry entries")
    if set(FORBIDDEN_OUTPUTS) - set(row.get("forbidden_outputs", []) if isinstance(row.get("forbidden_outputs"), list) else []):
        errors.append(f"row {index}: forbidden_outputs missing required registry entries")

    summary_hits = _contains_pattern(str(row.get("safe_summary", "")), FORBIDDEN_PUBLIC_CLAIM_PATTERNS)
    if summary_hits:
        errors.append(f"row {index}: safe_summary contains forbidden claim pattern(s): {summary_hits}")
    next_step_patterns = dict(FORBIDDEN_PUBLIC_CLAIM_PATTERNS)
    next_step_patterns.update(MANIPULATION_NEXT_STEP_PATTERNS)
    next_hits = _contains_pattern(str(row.get("safe_next_step", "")), next_step_patterns)
    if next_hits:
        errors.append(f"row {index}: safe_next_step contains unsafe claim or tactic pattern(s): {next_hits}")

    return errors


def aggregate_row_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_counts: Counter[str] = Counter(str(row.get("source_tier", "unknown")) for row in rows)
    split_counts: Counter[str] = Counter(str(row.get("split", "unknown")) for row in rows)
    cue_counts: Counter[str] = Counter()
    for row in rows:
        cue_counts.update(str(cue) for cue in row.get("expected_cues", []) if isinstance(cue, str))
    return {
        "row_count": len(rows),
        "source_counts": dict(sorted(source_counts.items())),
        "split_counts": dict(sorted(split_counts.items())),
        "cue_counts": dict(sorted(cue_counts.items())),
    }


def report_text_has_forbidden_claims(text: str) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in UNSAFE_PUBLIC_REPORT_PHRASES if phrase in lower]
