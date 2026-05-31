"""Deterministic observable cue taxonomy for Vibe Engine."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any, Iterable

from ..evidence.objects import build_evidence_object


CUE_IDS = {
    "directness",
    "specificity",
    "hedging",
    "urgency",
    "reassurance",
    "pressure",
    "conflict",
    "alignment",
    "response_timing",
    "topic_shift",
    "ambiguity",
    "cognitive_load",
    "unclear_ask",
    "overloaded_message",
    "escalation_risk",
    "repair_opportunity",
    "boundary_pressure",
    "consent_clarity",
}

DIRECTNESS_RE = re.compile(r"\b(please|can you|could you|will you|would you|i need|i want|confirm|send|review)\b", re.IGNORECASE)
SPECIFICITY_RE = re.compile(r"\b(\d{1,2}(:\d{2})?\s?(am|pm)?|monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tonight|tomorrow|before|by)\b", re.IGNORECASE)
HEDGING_RE = re.compile(r"\b(maybe|perhaps|sort of|kind of|i guess|not sure|might|could be|if you want)\b", re.IGNORECASE)
URGENCY_RE = re.compile(r"\b(right now|urgent|asap|immediately|before|by tonight|deadline|need this now)\b", re.IGNORECASE)
URGENCY_REDUCERS_RE = re.compile(r"\b(no rush|no hurry|when you can)\b", re.IGNORECASE)
REASSURANCE_RE = re.compile(r"\b(no rush|no pressure|when you can|it is okay|that's okay|all good)\b", re.IGNORECASE)
PRESSURE_RE = re.compile(r"\b(you must|right now|or else|if you do not|if you don't|you have to|don't say no|owe me)\b", re.IGNORECASE)
PRESSURE_REDUCERS_RE = re.compile(r"\b(no pressure|only if you want|when you can)\b", re.IGNORECASE)
CONFLICT_RE = re.compile(r"\b(upset|frustrated|argument|fight|disagree|not okay|hurt|sorry this got tense)\b", re.IGNORECASE)
ALIGNMENT_RE = re.compile(r"\b(i agree|that works|sounds good|same page|yes, that plan|aligned)\b", re.IGNORECASE)
TOPIC_SHIFT_RE = re.compile(r"\b(anyway|separately|another thing|new topic|switching topics)\b", re.IGNORECASE)
AMBIGUITY_RE = re.compile(r"\b(maybe|idk|not sure|whatever|sometime|later maybe|we'll see|unclear)\b", re.IGNORECASE)
REPAIR_RE = re.compile(r"\b(sorry|let me rephrase|reset|repair|misunderstood|i meant)\b", re.IGNORECASE)
BOUNDARY_PRESSURE_RE = re.compile(r"\b(send me your|share your|prove it|why won't you|don't tell anyone|private photo|your location|you have to)\b", re.IGNORECASE)
CONSENT_CLEAR_RE = re.compile(r"\b(yes|i consent|i'm okay with|i am okay with|only if you want|you can say no|do you consent|is that okay)\b", re.IGNORECASE)
CONSENT_MIXED_RE = re.compile(r"\b(not sure|maybe|i guess|only if|stop|do not|don't)\b", re.IGNORECASE)
ASK_RE = re.compile(r"\b(can|could|will|would)\s+you\b|\?|\bplease\b|\bconfirm\b", re.IGNORECASE)


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


def _first_match(pattern: re.Pattern[str], text: str) -> tuple[int, int, str] | None:
    match = pattern.search(text)
    if not match:
        return None
    return match.start(), match.end(), match.group(0)


def _evidence(
    *,
    cue_id: str,
    message: dict[str, Any],
    text: str,
    start: int = 0,
    end: int | None = None,
    evidence_text: str | None = None,
    strength: int = 1,
    conversation_id: str,
    state: str | None = None,
) -> dict[str, Any]:
    evidence = evidence_text if evidence_text is not None else text
    if end is None:
        end = start + len(evidence)
    row = build_evidence_object(
        evidence_id=f"{conversation_id}_{message.get('id', message.get('message_id', 'message'))}_{cue_id}",
        conversation_id=conversation_id,
        source_type="synthetic_fixture" if str(conversation_id).startswith("synthetic") else "manual_local",
        message_id=message.get("id", message.get("message_id", "")),
        turn_id=message.get("turn_id", message.get("id", message.get("message_id", ""))),
        speaker_role=str(message.get("speaker_role", message.get("author", "unknown"))),
        cue_name=cue_id,
        evidence_text=evidence,
        start_offset=max(0, int(start)),
        end_offset=max(0, int(end)),
        provenance={
            "source": "deterministic_cue_taxonomy",
            "note": "Quoted lines and code blocks are excluded before cue detection.",
        },
    )
    row["cue_id"] = cue_id
    row["strength"] = int(strength)
    if state:
        row["state"] = state
    return row


def _add_pattern_cue(
    cues: list[dict[str, Any]],
    *,
    cue_id: str,
    pattern: re.Pattern[str],
    text: str,
    message: dict[str, Any],
    conversation_id: str,
    strength: int = 2,
    reducer: re.Pattern[str] | None = None,
) -> None:
    if reducer and reducer.search(text):
        return
    match = _first_match(pattern, text)
    if match:
        start, end, evidence = match
        cues.append(
            _evidence(
                cue_id=cue_id,
                message=message,
                text=text,
                start=start,
                end=end,
                evidence_text=evidence,
                strength=strength,
                conversation_id=conversation_id,
            )
        )


def _message_cues(message: dict[str, Any], conversation_id: str) -> list[dict[str, Any]]:
    text = _strip_quotes_and_code(str(message.get("text", "")))
    if not text:
        return []

    cues: list[dict[str, Any]] = []
    _add_pattern_cue(cues, cue_id="directness", pattern=DIRECTNESS_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="specificity", pattern=SPECIFICITY_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="hedging", pattern=HEDGING_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="urgency", pattern=URGENCY_RE, text=text, message=message, conversation_id=conversation_id, reducer=URGENCY_REDUCERS_RE)
    _add_pattern_cue(cues, cue_id="reassurance", pattern=REASSURANCE_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="pressure", pattern=PRESSURE_RE, text=text, message=message, conversation_id=conversation_id, reducer=PRESSURE_REDUCERS_RE)
    _add_pattern_cue(cues, cue_id="conflict", pattern=CONFLICT_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="alignment", pattern=ALIGNMENT_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="topic_shift", pattern=TOPIC_SHIFT_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="ambiguity", pattern=AMBIGUITY_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="repair_opportunity", pattern=REPAIR_RE, text=text, message=message, conversation_id=conversation_id)
    _add_pattern_cue(cues, cue_id="boundary_pressure", pattern=BOUNDARY_PRESSURE_RE, text=text, message=message, conversation_id=conversation_id)

    if _word_count(text) >= 36 or _sentence_count(text) >= 4 or text.count("?") >= 2:
        cues.append(_evidence(cue_id="cognitive_load", message=message, text=text, strength=2, conversation_id=conversation_id))
        cues.append(_evidence(cue_id="overloaded_message", message=message, text=text, strength=2, conversation_id=conversation_id))

    if not ASK_RE.search(text) and (AMBIGUITY_RE.search(text) or _word_count(text) <= 5):
        cues.append(_evidence(cue_id="unclear_ask", message=message, text=text, strength=2, conversation_id=conversation_id))

    consent_clear = CONSENT_CLEAR_RE.search(text)
    consent_mixed = CONSENT_MIXED_RE.search(text)
    if consent_clear or consent_mixed:
        state = "mixed" if consent_clear and consent_mixed else "clear" if consent_clear else "unclear"
        match = consent_clear or consent_mixed
        cues.append(
            _evidence(
                cue_id="consent_clarity",
                message=message,
                text=text,
                start=match.start(),
                end=match.end(),
                evidence_text=match.group(0),
                strength=2,
                conversation_id=conversation_id,
                state=state,
            )
        )

    cue_ids = {cue["cue_id"] for cue in cues}
    if "pressure" in cue_ids and ({"conflict", "boundary_pressure"} & cue_ids):
        cues.append(_evidence(cue_id="escalation_risk", message=message, text=text, strength=2, conversation_id=conversation_id))

    return cues


def _response_timing_cues(messages: list[dict[str, Any]], conversation_id: str) -> list[dict[str, Any]]:
    cues: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    previous_time: datetime | None = None
    for message in messages:
        current_time = _parse_time(message.get("created_at"))
        if previous and previous_time and current_time:
            same_author = str(previous.get("author", previous.get("speaker_role", ""))) == str(message.get("author", message.get("speaker_role", "")))
            delta = (current_time - previous_time).total_seconds()
            if same_author and 0 <= delta <= 180:
                text = _strip_quotes_and_code(str(message.get("text", ""))) or str(message.get("text", ""))
                cues.append(_evidence(cue_id="response_timing", message=message, text=text, strength=2, conversation_id=conversation_id))
        previous = message
        previous_time = current_time
    return cues


def detect_cues(messages: Iterable[dict[str, Any]], *, conversation_id: str = "synthetic_cue_fixture") -> list[dict[str, Any]]:
    materialized = [dict(message) for message in messages]
    cues: list[dict[str, Any]] = []
    for message in materialized:
        cues.extend(_message_cues(message, conversation_id))
    cues.extend(_response_timing_cues(materialized, conversation_id))
    return cues
