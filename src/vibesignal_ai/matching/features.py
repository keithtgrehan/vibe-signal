"""Deterministic observable features for Vibe matching."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from typing import Any

from ..features.cue_taxonomy import detect_cues
from ..features.shared import (
    content_tokens,
    count_pattern_hits,
    is_question,
    responsiveness_score,
    safe_excerpt,
    specificity_score,
    word_count,
)


VAGUE_RE = re.compile(r"\b(?:maybe|later|soon|stuff|things|not sure|sometime|we'?ll see|idk|whatever)\b", re.IGNORECASE)
UNSUPPORTED_CLAIM_RE = re.compile(
    r"\b(?:you always|you never|obviously|everyone knows|that proves|you don'?t care|you are trying to|you'?re trying to)\b",
    re.IGNORECASE,
)
DIRECT_ANSWER_RE = re.compile(
    r"^\s*(?:yes|yeah|yep|no|ok|okay|sure|confirmed|not confirmed|that works|sounds good|works for me|i can|i can't|i cannot|i will|i won'?t|we can|we can'?t)\b",
    re.IGNORECASE,
)
WORKS_REPLY_RE = re.compile(r"\bworks\b", re.IGNORECASE)
TOPIC_SHIFT_RE = re.compile(r"\b(?:anyway|separately|another thing|new topic|switching topics)\b", re.IGNORECASE)
CLARIFYING_REPLY_RE = re.compile(
    r"\b(?:one request first|answer clearly|can you clarify|could you clarify|which part|what do you mean|send one request|split this into|one thing at a time)\b",
    re.IGNORECASE,
)
TIME_DETAIL_RE = re.compile(
    r"\b(?:(?:\d{1,2}:\d{2}\s?(?:am|pm)?|\d{1,2}\s?(?:am|pm))|monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tonight|tomorrow|weekend)\b",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(r"\b\d+(?::\d+)?\b")
BOUNDARY_RESPECT_RE = re.compile(r"\b(?:you can say no|only if you want|no pressure|is that okay|if that works for you)\b", re.IGNORECASE)
CONTRADICTION_PATTERNS = (
    (re.compile(r"\bi can(?!['’]?t|not)\b", re.IGNORECASE), re.compile(r"\bi (?:can['’]?t|cannot)\b", re.IGNORECASE)),
    (re.compile(r"\bi will\b", re.IGNORECASE), re.compile(r"\bi won'?t\b", re.IGNORECASE)),
    (re.compile(r"\bfree\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.IGNORECASE), re.compile(r"\bnot free\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.IGNORECASE)),
    (re.compile(r"\bconfirmed\b", re.IGNORECASE), re.compile(r"\bnot confirmed\b", re.IGNORECASE)),
)


@dataclass(frozen=True)
class MatchingFeatures:
    cue_counts: Counter[str]
    taxonomy_evidence: list[dict[str, Any]]
    custom_evidence: list[dict[str, Any]]
    specificity_drop: list[dict[str, Any]]
    answer_evasion_pattern: list[dict[str, Any]]
    contradiction_against_prior_message: list[dict[str, Any]]
    unsupported_claim_shift: list[dict[str, Any]]
    boundary_respect_count: int
    vague_message_count: int
    total_word_count: int
    one_sided: bool
    missing_timestamp_count: int

    @property
    def inconsistency_cues(self) -> list[dict[str, Any]]:
        return [
            *self.contradiction_against_prior_message,
            *self.specificity_drop,
            *self.unsupported_claim_shift,
            *self.answer_evasion_pattern,
        ]

    @property
    def all_evidence(self) -> list[dict[str, Any]]:
        return [*self.taxonomy_evidence, *self.custom_evidence]


def _message_id(message: dict[str, Any]) -> str:
    return str(message.get("id") or message.get("message_id") or "message")


def _feature_evidence(
    *,
    conversation_id: str,
    message: dict[str, Any],
    cue_family: str,
    safe_phrase: str,
    explanation: str,
    evidence_text: str | None = None,
    source_message_id: str | None = None,
    strength: int = 2,
) -> dict[str, Any]:
    text = " ".join(str(evidence_text if evidence_text is not None else message.get("text", "")).split())
    start = max(0, str(message.get("text", "")).find(text)) if text else 0
    if start < 0:
        start = 0
    message_id = _message_id(message)
    return {
        "evidence_id": f"{conversation_id}_{message_id}_{cue_family}_{start}",
        "conversation_id": conversation_id,
        "message_id": message_id,
        "source_message_id": source_message_id or message_id,
        "speaker_role": str(message.get("author", message.get("speaker_role", "unknown"))),
        "cue_id": cue_family,
        "cue_family": cue_family,
        "evidence_text": text,
        "span_start": start,
        "span_end": start + len(text),
        "confidence": 0.68,
        "strength": int(strength),
        "safe_phrase": safe_phrase,
        "explanation": explanation,
        "interpretation_limits": {
            "does_not_infer_true_emotion": True,
            "does_not_detect_deception": True,
            "does_not_score_personality": True,
        },
    }


def concrete_detail_count(text: str) -> int:
    tokens = content_tokens(text)
    return (
        len(TIME_DETAIL_RE.findall(str(text or "")))
        + len(NUMBER_RE.findall(str(text or "")))
        + sum(1 for token in tokens if len(token) >= 5)
    )


def _has_direct_ask(text: str) -> bool:
    lowered = str(text or "").lower()
    return is_question(lowered) or any(marker in lowered for marker in ("can you", "could you", "will you", "would you", "please confirm", "confirm"))


def _is_evasive_reply(previous: str, current: str) -> bool:
    if not _has_direct_ask(previous):
        return False
    if CLARIFYING_REPLY_RE.search(current):
        return False
    if DIRECT_ANSWER_RE.search(current) and not TOPIC_SHIFT_RE.search(current):
        return False
    if WORKS_REPLY_RE.search(current) and responsiveness_score(previous, current) >= 0.08 and not TOPIC_SHIFT_RE.search(current):
        return False
    overlap = responsiveness_score(previous, current)
    vague = bool(VAGUE_RE.search(current))
    topic_shift = bool(TOPIC_SHIFT_RE.search(current))
    reassurance_without_answer = "all good" in current.lower() or "no worries" in current.lower()
    return overlap < 0.18 or vague or topic_shift or reassurance_without_answer


def detect_specificity_drops(messages: list[dict[str, Any]], conversation_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for previous, current in zip(messages, messages[1:]):
        if previous.get("author") == current.get("author"):
            continue
        previous_text = str(previous.get("text", ""))
        current_text = str(current.get("text", ""))
        previous_detail = concrete_detail_count(previous_text)
        current_detail = concrete_detail_count(current_text)
        previous_numbers = len(NUMBER_RE.findall(previous_text))
        current_numbers = len(NUMBER_RE.findall(current_text))
        previous_time_details = len(TIME_DETAIL_RE.findall(previous_text))
        current_time_details = len(TIME_DETAIL_RE.findall(current_text))
        previous_specificity = specificity_score(previous_text)
        current_specificity = specificity_score(current_text)
        direct_acknowledgement = bool(DIRECT_ANSWER_RE.search(current_text))
        clarifying_reply = bool(CLARIFYING_REPLY_RE.search(current_text))
        concrete_drop = (
            current_detail < previous_detail
            or current_specificity + 0.18 < previous_specificity
            or current_numbers < previous_numbers
            or current_time_details < previous_time_details
        )
        if _has_direct_ask(previous_text) and not direct_acknowledgement and not clarifying_reply and previous_detail >= 2 and concrete_drop and (
            VAGUE_RE.search(current_text) or word_count(current_text) <= max(5, word_count(previous_text) // 2)
        ):
            rows.append(
                _feature_evidence(
                    conversation_id=conversation_id,
                    message=current,
                    cue_family="specificity_drop",
                    safe_phrase="Later reply has fewer concrete details than the earlier ask.",
                    explanation="Deterministic detail-count comparison found fewer concrete details in the later reply.",
                    source_message_id=_message_id(previous),
                    strength=2,
                )
            )
    return rows


def detect_answer_evasion(messages: list[dict[str, Any]], conversation_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for previous, current in zip(messages, messages[1:]):
        if previous.get("author") == current.get("author"):
            continue
        previous_text = str(previous.get("text", ""))
        current_text = str(current.get("text", ""))
        if _is_evasive_reply(previous_text, current_text):
            rows.append(
                _feature_evidence(
                    conversation_id=conversation_id,
                    message=current,
                    cue_family="answer_evasion_pattern",
                    safe_phrase="The reply does not directly answer the previous ask.",
                    explanation="A direct ask was followed by a reply with low topic overlap, vague deferral, or topic-shift wording.",
                    source_message_id=_message_id(previous),
                    strength=2,
                )
            )
    return rows


def detect_unsupported_claim_shifts(messages: list[dict[str, Any]], conversation_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for message in messages:
        text = str(message.get("text", ""))
        match = UNSUPPORTED_CLAIM_RE.search(text)
        if not match:
            continue
        rows.append(
            _feature_evidence(
                conversation_id=conversation_id,
                message=message,
                cue_family="unsupported_claim_shift",
                safe_phrase="This message introduces a strong claim without concrete supporting detail.",
                explanation="A strong generalizing claim was found without nearby concrete support.",
                evidence_text=match.group(0),
                strength=2,
            )
        )
    return rows


def detect_contradictions(messages: list[dict[str, Any]], conversation_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, current in enumerate(messages):
        current_text = str(current.get("text", ""))
        for previous in messages[:index]:
            if previous.get("author") != current.get("author"):
                continue
            previous_text = str(previous.get("text", ""))
            matched = False
            for positive, negative in CONTRADICTION_PATTERNS:
                if positive.search(previous_text) and negative.search(current_text):
                    matched = True
                    break
                if negative.search(previous_text) and positive.search(current_text):
                    matched = True
                    break
            if not matched:
                continue
            shared = content_tokens(previous_text) & content_tokens(current_text)
            if not shared and not ({day.lower() for day in TIME_DETAIL_RE.findall(previous_text)} & {day.lower() for day in TIME_DETAIL_RE.findall(current_text)}):
                continue
            rows.append(
                _feature_evidence(
                    conversation_id=conversation_id,
                    message=current,
                    cue_family="contradiction_against_prior_message",
                    safe_phrase="This reply conflicts with an earlier stated availability/commitment.",
                    explanation="A deterministic pattern comparison found a later commitment or availability reversal.",
                    source_message_id=_message_id(previous),
                    strength=2,
                )
            )
            break
    return rows


def extract_matching_features(messages: list[dict[str, Any]], *, conversation_id: str) -> MatchingFeatures:
    taxonomy_evidence = detect_cues(messages, conversation_id=conversation_id)
    cue_counts = Counter(str(cue.get("cue_family")) for cue in taxonomy_evidence)
    specificity_drop = detect_specificity_drops(messages, conversation_id)
    answer_evasion_pattern = detect_answer_evasion(messages, conversation_id)
    contradiction_against_prior_message = detect_contradictions(messages, conversation_id)
    unsupported_claim_shift = detect_unsupported_claim_shifts(messages, conversation_id)
    custom_evidence = [
        *specificity_drop,
        *answer_evasion_pattern,
        *contradiction_against_prior_message,
        *unsupported_claim_shift,
    ]
    for row in custom_evidence:
        cue_counts[str(row.get("cue_family"))] += 1

    authors = {str(message.get("author", "unknown")) for message in messages if str(message.get("author", "unknown")) != "unknown"}
    return MatchingFeatures(
        cue_counts=cue_counts,
        taxonomy_evidence=taxonomy_evidence,
        custom_evidence=custom_evidence,
        specificity_drop=specificity_drop,
        answer_evasion_pattern=answer_evasion_pattern,
        contradiction_against_prior_message=contradiction_against_prior_message,
        unsupported_claim_shift=unsupported_claim_shift,
        boundary_respect_count=sum(1 for message in messages if BOUNDARY_RESPECT_RE.search(str(message.get("text", "")))),
        vague_message_count=sum(1 for message in messages if VAGUE_RE.search(str(message.get("text", "")))),
        total_word_count=sum(word_count(str(message.get("text", ""))) for message in messages),
        one_sided=len(authors) <= 1,
        missing_timestamp_count=sum(1 for message in messages if not message.get("created_at")),
    )


def evidence_preview(row: dict[str, Any]) -> str:
    return safe_excerpt(str(row.get("evidence_text", "")), limit=90)
