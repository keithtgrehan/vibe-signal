"""Deterministic observable cue taxonomy for Vibe Signal."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any, Iterable

import yaml

from ..evidence.objects import build_evidence_object


CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "vibe_cue_taxonomy.yml"
ASK_RE = re.compile(r"\b(can|could|will|would)\s+you\b|\?|\bplease\b|\bconfirm\b", re.IGNORECASE)
REQUEST_MARKER_RE = re.compile(r"\b(?:can you|could you|will you|would you|please|confirm|send|review|check|compare|rewrite|tell me)\b", re.IGNORECASE)
ACTION_OR_DECISION_RE = re.compile(
    r"\b(?:confirm|send|review|check|compare|rewrite|tell me|meet|call|reply|answer|decide|choose|bring|share|explain|plan|need|deadline)\b",
    re.IGNORECASE,
)
VAGUE_OR_HEDGE_RE = re.compile(r"\b(?:maybe|idk|not sure|whatever|sometime|later|we'll see|unclear)\b", re.IGNORECASE)
LOW_PRESSURE_COMMAND_RE = re.compile(r"\b(?:no rush|no pressure|no stress|when you can)\b", re.IGNORECASE)
STRONG_DIRECT_MARKER_RE = re.compile(r"\b(?:please|can you|could you|will you|would you|i need|i want|please confirm|did you|do you|are you)\b", re.IGNORECASE)
PRESSURE_DIRECTIVE_RE = re.compile(r"\b(?:you have to|you must|right now|or else|owe me|don't say no)\b", re.IGNORECASE)
ESCALATION_MARKER_RE = re.compile(
    r"\b(?:or else|you always|you never|your fault|stop asking|not okay|fight|argument|right now)\b|[!?]{2,}|\b[A-Z]{3,}\b",
    re.IGNORECASE,
)
INTENSE_PUNCTUATION_RE = re.compile(r"[!?]{2,}|\b[A-Z]{3,}\b")


@dataclass(frozen=True)
class CueRule:
    cue_id: str
    cue_family: str
    patterns: tuple[re.Pattern[str], ...]
    reducers: tuple[re.Pattern[str], ...]
    confidence: float
    explanation: str
    safe_phrase: str
    computed_rule: str | None = None


def _load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _compile_rule(row: dict[str, Any]) -> CueRule:
    return CueRule(
        cue_id=str(row["cue_id"]),
        cue_family=str(row["cue_family"]),
        patterns=tuple(re.compile(pattern, re.IGNORECASE) for pattern in row.get("patterns", [])),
        reducers=tuple(re.compile(pattern, re.IGNORECASE) for pattern in row.get("reducers", [])),
        confidence=float(row.get("confidence", 0.7)),
        explanation=str(row["explanation"]),
        safe_phrase=str(row["safe_phrase"]),
        computed_rule=row.get("computed_rule"),
    )


def load_taxonomy_rules(path: Path = CONFIG_PATH) -> dict[str, CueRule]:
    payload = _load_config(path)
    rows = payload.get("cues", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError("Cue taxonomy config must contain a non-empty cues list.")
    compiled = [_compile_rule(row) for row in rows]
    rules = {rule.cue_family: rule for rule in compiled}
    if len(rules) != len(rows):
        raise ValueError("Cue taxonomy contains duplicate cue_family values.")
    return rules


RULES_BY_FAMILY = load_taxonomy_rules()
CUE_IDS = set(RULES_BY_FAMILY)


def _strip_quotes_and_code(text: str) -> str:
    visible: list[str] = []
    in_code = False
    for line in str(text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or stripped.startswith(">"):
            continue
        visible.append(line)
    return "\n".join(visible).strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def _sentence_count(text: str) -> int:
    return len([part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()])


def _request_marker_count(text: str) -> int:
    return len(REQUEST_MARKER_RE.findall(text))


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value)
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def _first_match(rule: CueRule, text: str) -> re.Match[str] | None:
    if any(reducer.search(text) for reducer in rule.reducers):
        return None
    for pattern in rule.patterns:
        match = pattern.search(text)
        if match:
            return match
    return None


def _has_direct_request_or_decision(text: str) -> bool:
    lowered = str(text or "").lower()
    return bool(ASK_RE.search(lowered) or REQUEST_MARKER_RE.search(lowered) or lowered.strip().startswith(("yes", "no", "i can", "i can't", "i cannot", "i will", "i won't", "we can", "we can't")))


def _specificity_context_is_actionable(text: str) -> bool:
    lowered = str(text or "").lower()
    return bool(_has_direct_request_or_decision(lowered) or ACTION_OR_DECISION_RE.search(lowered) or "available" in lowered or "works" in lowered)


def _unclear_ask_context(text: str) -> bool:
    lowered = str(text or "").lower()
    if not ASK_RE.search(lowered):
        return False
    if not VAGUE_OR_HEDGE_RE.search(lowered):
        return False
    return not ACTION_OR_DECISION_RE.search(lowered)


def _evidence(
    *,
    rule: CueRule,
    message: dict[str, Any],
    text: str,
    start: int = 0,
    end: int | None = None,
    evidence_text: str | None = None,
    conversation_id: str,
    strength: int = 2,
    state: str | None = None,
) -> dict[str, Any]:
    evidence = evidence_text if evidence_text is not None else text
    if end is None:
        end = start + len(evidence)
    message_id = message.get("id", message.get("message_id", "message"))
    row = build_evidence_object(
        evidence_id=f"{conversation_id}_{message_id}_{rule.cue_id}_{max(0, int(start))}",
        conversation_id=conversation_id,
        source_type="synthetic_fixture" if str(conversation_id).startswith("synthetic") else "manual_local",
        message_id=message_id,
        turn_id=message.get("turn_id", message_id),
        speaker_role=str(message.get("speaker_role", message.get("author", "unknown"))),
        cue_name=rule.cue_id,
        cue_id=rule.cue_id,
        cue_family=rule.cue_family,
        evidence_text=evidence,
        start_offset=max(0, int(start)),
        end_offset=max(0, int(end)),
        span_start=max(0, int(start)),
        span_end=max(0, int(end)),
        confidence=rule.confidence,
        explanation=rule.explanation,
        safe_phrase=rule.safe_phrase,
        provenance={
            "source": "deterministic_vibe_cue_taxonomy",
            "taxonomy_config": str(CONFIG_PATH.relative_to(Path(__file__).resolve().parents[3])),
            "note": "Quoted lines and code blocks are excluded before cue detection.",
        },
    )
    row["strength"] = int(strength)
    if state:
        row["state"] = state
    return row


def _add_pattern_cue(
    cues: list[dict[str, Any]],
    *,
    cue_family: str,
    text: str,
    message: dict[str, Any],
    conversation_id: str,
    strength: int = 2,
) -> None:
    rule = RULES_BY_FAMILY[cue_family]
    match = _first_match(rule, text)
    if not match:
        return
    if cue_family == "directness" and PRESSURE_DIRECTIVE_RE.search(text):
        return
    if cue_family == "directness" and LOW_PRESSURE_COMMAND_RE.search(text) and not STRONG_DIRECT_MARKER_RE.search(text):
        return
    if cue_family == "directness" and VAGUE_OR_HEDGE_RE.search(text) and not ACTION_OR_DECISION_RE.search(text):
        return
    if cue_family == "hedging" and match.group(0).lower() == "i think" and not (
        ACTION_OR_DECISION_RE.search(text) or "works" in str(text or "").lower()
    ):
        return
    if cue_family == "urgency" and match.group(0).lower().startswith("by ") and not STRONG_DIRECT_MARKER_RE.search(text):
        return
    if cue_family == "specificity" and not _specificity_context_is_actionable(text):
        return
    cues.append(
        _evidence(
            rule=rule,
            message=message,
            text=text,
            start=match.start(),
            end=match.end(),
            evidence_text=match.group(0),
            strength=strength,
            conversation_id=conversation_id,
        )
    )


def _message_is_overloaded(text: str) -> bool:
    comma_list_count = str(text or "").count(",")
    conjunction_count = len(re.findall(r"\b(?:and|whether)\b", str(text or ""), flags=re.IGNORECASE))
    return (
        _word_count(text) >= 30
        or _sentence_count(text) >= 4
        or text.count("?") >= 2
        or _request_marker_count(text) >= 4
        or (comma_list_count >= 4 and conjunction_count >= 1 and _word_count(text) >= 14)
    )


def _add_whole_message_cue(
    cues: list[dict[str, Any]],
    *,
    cue_family: str,
    text: str,
    message: dict[str, Any],
    conversation_id: str,
    strength: int = 2,
) -> None:
    cues.append(
        _evidence(
            rule=RULES_BY_FAMILY[cue_family],
            message=message,
            text=text,
            conversation_id=conversation_id,
            strength=strength,
        )
    )


def _message_cues(message: dict[str, Any], conversation_id: str) -> list[dict[str, Any]]:
    text = _strip_quotes_and_code(str(message.get("text", "")))
    if not text:
        return []

    cues: list[dict[str, Any]] = []
    for cue_family in (
        "directness",
        "specificity",
        "hedging",
        "urgency",
        "reassurance",
        "pressure",
        "conflict",
        "alignment",
        "ambiguity",
        "repair_opportunity",
        "boundary_pressure",
        "consent_clarity",
    ):
        _add_pattern_cue(cues, cue_family=cue_family, text=text, message=message, conversation_id=conversation_id)

    if _message_is_overloaded(text):
        _add_whole_message_cue(cues, cue_family="cognitive_load", text=text, message=message, conversation_id=conversation_id)
        _add_whole_message_cue(cues, cue_family="overloaded_message", text=text, message=message, conversation_id=conversation_id)

    if "ambiguity" in {cue["cue_family"] for cue in cues} and _unclear_ask_context(text):
        _add_whole_message_cue(cues, cue_family="unclear_ask", text=text, message=message, conversation_id=conversation_id)

    cue_families = {cue["cue_family"] for cue in cues}
    pressure_escalation = "pressure" in cue_families and ({"conflict", "boundary_pressure"} & cue_families) and ESCALATION_MARKER_RE.search(text)
    conflict_intensity = "conflict" in cue_families and INTENSE_PUNCTUATION_RE.search(text)
    if pressure_escalation or conflict_intensity:
        _add_whole_message_cue(cues, cue_family="escalation_risk", text=text, message=message, conversation_id=conversation_id)

    return cues


def _topic_shift_cues(messages: list[dict[str, Any]], conversation_id: str) -> list[dict[str, Any]]:
    cues: list[dict[str, Any]] = []
    rule = RULES_BY_FAMILY["topic_shift"]
    previous: dict[str, Any] | None = None
    for message in messages:
        text = _strip_quotes_and_code(str(message.get("text", "")))
        if previous:
            previous_text = _strip_quotes_and_code(str(previous.get("text", "")))
            different_author = str(previous.get("author", previous.get("speaker_role", ""))) != str(message.get("author", message.get("speaker_role", "")))
            match = _first_match(rule, text)
            if different_author and ASK_RE.search(previous_text) and match:
                cues.append(
                    _evidence(
                        rule=rule,
                        message=message,
                        text=text,
                        start=match.start(),
                        end=match.end(),
                        evidence_text=match.group(0),
                        conversation_id=conversation_id,
                    )
                )
        previous = message
    return cues


def _response_timing_cues(messages: list[dict[str, Any]], conversation_id: str) -> list[dict[str, Any]]:
    cues: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    previous_time: datetime | None = None
    for message in messages:
        current_time = _parse_time(message.get("created_at"))
        if previous and previous_time and current_time:
            previous_author = str(previous.get("author", previous.get("speaker_role", "")))
            current_author = str(message.get("author", message.get("speaker_role", "")))
            delta = (current_time - previous_time).total_seconds()
            if previous_author == current_author and 0 <= delta <= 180:
                text = _strip_quotes_and_code(str(message.get("text", ""))) or str(message.get("text", ""))
                _add_whole_message_cue(cues, cue_family="response_timing", text=text, message=message, conversation_id=conversation_id)
        previous = message
        previous_time = current_time
    return cues


def detect_cues(messages: Iterable[dict[str, Any]], *, conversation_id: str = "synthetic_cue_fixture") -> list[dict[str, Any]]:
    materialized = [dict(message) for message in messages]
    cues: list[dict[str, Any]] = []
    for message in materialized:
        cues.extend(_message_cues(message, conversation_id))
    cues.extend(_topic_shift_cues(materialized, conversation_id))
    cues.extend(_response_timing_cues(materialized, conversation_id))
    return cues
