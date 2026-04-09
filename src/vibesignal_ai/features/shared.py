"""Shared deterministic heuristics for conversation analysis."""

from __future__ import annotations

from datetime import datetime
import math
import re
from statistics import mean, pstdev
from typing import Any

from ..nlp.sentence_split import sentence_stats
from ..nlp.spacy_features import analyze_spacy_structure

WORD_RE = re.compile(r"[A-Za-z0-9']+")
NUMBER_RE = re.compile(r"\b\d+(?::\d+)?\b")
TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3])(?::[0-5]\d)?\s?(?:am|pm)?\b", re.IGNORECASE)
DAY_RE = re.compile(
    r"\b(today|tonight|tomorrow|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend)\b",
    re.IGNORECASE,
)
QUESTION_CUES = ("?", "can you", "could you", "are you", "did you", "will you", "what", "why", "when", "how")
STOPWORDS = {
    "the", "a", "an", "is", "are", "to", "and", "or", "i", "you", "we", "it",
    "of", "in", "on", "for", "this", "that", "be", "with", "at", "my", "your",
}
TOKEN_SYNONYMS = {
    "coming": "arrive",
    "come": "arrive",
    "there": "arrive",
    "job": "work",
    "office": "work",
    "home": "place",
    "restaurant": "place",
    "call": "talk",
    "phone": "talk",
    "text": "talk",
    "message": "talk",
    "confirm": "answer",
    "let": "answer",
    "know": "answer",
}
UNCERTAINTY_MARKERS = (
    re.compile(r"\bmaybe\b", re.IGNORECASE),
    re.compile(r"\bperhaps\b", re.IGNORECASE),
    re.compile(r"\bprobably\b", re.IGNORECASE),
    re.compile(r"\bi think\b", re.IGNORECASE),
    re.compile(r"\bi guess\b", re.IGNORECASE),
    re.compile(r"\bnot sure\b", re.IGNORECASE),
    re.compile(r"\bmight\b", re.IGNORECASE),
    re.compile(r"\bcould be\b", re.IGNORECASE),
)
HEDGE_PATTERNS = UNCERTAINTY_MARKERS + (
    re.compile(r"\bkind of\b", re.IGNORECASE),
    re.compile(r"\bsort of\b", re.IGNORECASE),
    re.compile(r"\bmaybe later\b", re.IGNORECASE),
    re.compile(r"\bit depends\b", re.IGNORECASE),
)
AVOIDANCE_PATTERNS = (
    re.compile(r"\bit depends\b", re.IGNORECASE),
    re.compile(r"\bwe'?ll see\b", re.IGNORECASE),
    re.compile(r"\bprefer not\b", re.IGNORECASE),
    re.compile(r"\bhard to say\b", re.IGNORECASE),
    re.compile(r"\blet'?s not get into that\b", re.IGNORECASE),
    re.compile(r"\bnot getting into\b", re.IGNORECASE),
    re.compile(r"\bmaybe later\b", re.IGNORECASE),
    re.compile(r"\banother time\b", re.IGNORECASE),
)
REASSURANCE_WORDS = {"okay", "alright", "fine", "good", "sure", "definitely", "absolutely", "promise", "glad"}
CONFLICT_WORDS = {"angry", "upset", "mad", "frustrated", "annoyed", "argument", "fight", "hard", "stress", "concerned"}
ACTION_VERBS = {"go", "meet", "call", "text", "leave", "arrive", "book", "send", "bring", "pick", "finish", "start", "plan"}
PLACE_TERMS = {"home", "office", "work", "restaurant", "station", "airport", "school", "gym", "house", "hotel"}
EVENT_TERMS = {"dinner", "meeting", "trip", "flight", "interview", "call", "appointment", "date", "plan", "weekend"}
VAGUE_TERMS = {"thing", "stuff", "something", "whatever", "anything", "maybe this"}
EXPLANATION_MARKERS = ("because", "so that", "the reason", "which means", "since")
DIRECT_OPENINGS = ("yes", "no", "i will", "i can", "i did", "i am", "we will", "we can", "because")
REVERSAL_PATTERNS = (
    re.compile(r"\bactually\b", re.IGNORECASE),
    re.compile(r"\bon second thought\b", re.IGNORECASE),
    re.compile(r"\binstead\b", re.IGNORECASE),
    re.compile(r"\bnot anymore\b", re.IGNORECASE),
    re.compile(r"\bchange of plans\b", re.IGNORECASE),
)
TOPIC_SHIFT_MARKERS = (
    re.compile(r"\banyway\b", re.IGNORECASE),
    re.compile(r"\bseparately\b", re.IGNORECASE),
    re.compile(r"\banother thing\b", re.IGNORECASE),
)
SELF_CORRECTION_MARKERS = (
    re.compile(r"\bi mean\b", re.IGNORECASE),
    re.compile(r"\bsorry\b", re.IGNORECASE),
    re.compile(r"\brather\b", re.IGNORECASE),
    re.compile(r"\blet me rephrase\b", re.IGNORECASE),
    re.compile(r"\bno,\s*i\b", re.IGNORECASE),
)
PUNCTUATION_REPEAT_RE = re.compile(r"([!?])\1+")
ELLIPSIS_RE = re.compile(r"\.\.\.+")
CAPS_TOKEN_RE = re.compile(r"\b[A-Z]{3,}\b")

WINDOW_SIGNAL_WEIGHTS = {
    "affect_balance": 0.12,
    "uncertainty": 0.11,
    "reassurance": 0.08,
    "conflict": 0.1,
    "directness": 0.16,
    "specificity": 0.16,
    "hedging": 0.12,
    "reply_length": 0.08,
    "response_latency": 0.09,
    "punctuation_emphasis": 0.08,
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def average(values: list[float]) -> float:
    return float(mean(values)) if values else 0.0


def stddev(values: list[float]) -> float:
    return float(pstdev(values)) if len(values) > 1 else 0.0


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in WORD_RE.findall(str(text or ""))]


def _normalized_token(token: str) -> str:
    lowered = token.lower()
    return TOKEN_SYNONYMS.get(lowered, lowered)


def content_tokens(text: str) -> set[str]:
    return {
        _normalized_token(token)
        for token in tokenize(text)
        if _normalized_token(token) not in STOPWORDS
    }


def word_count(text: str) -> int:
    return len(tokenize(text))


def is_question(text: str) -> bool:
    lowered = str(text or "").strip().lower()
    if not lowered:
        return False
    return "?" in lowered or any(lowered.startswith(cue) for cue in QUESTION_CUES if cue != "?")


def safe_excerpt(text: str, limit: int = 90) -> str:
    collapsed = " ".join(str(text or "").split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "…"


def count_pattern_hits(patterns: tuple[re.Pattern[str], ...], text: str) -> int:
    return sum(len(pattern.findall(str(text or ""))) for pattern in patterns)


def uncertainty_density(text: str) -> float:
    words = word_count(text)
    if words == 0:
        return 0.0
    return count_pattern_hits(UNCERTAINTY_MARKERS, text) / words


def hedge_count(text: str) -> int:
    return count_pattern_hits(HEDGE_PATTERNS, text)


def hedging_density(text: str) -> float:
    words = word_count(text)
    if words == 0:
        return 0.0
    return hedge_count(text) / words


def avoidance_markers(text: str) -> list[str]:
    matches: list[str] = []
    value = str(text or "")
    for pattern in AVOIDANCE_PATTERNS:
        if pattern.search(value):
            matches.append(pattern.pattern.replace("\\b", "").replace("\\", ""))
    return matches


def contradiction_markers(text: str) -> list[str]:
    matches: list[str] = []
    value = str(text or "")
    for pattern in REVERSAL_PATTERNS:
        if pattern.search(value):
            matches.append(pattern.pattern.replace("\\b", "").replace("\\", ""))
    return matches


def reassurance_score(text: str) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    return sum(1 for token in tokens if token in REASSURANCE_WORDS) / len(tokens)


def conflict_score(text: str) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    return sum(1 for token in tokens if token in CONFLICT_WORDS) / len(tokens)


def affect_balance_score(text: str) -> float:
    reassurance = reassurance_score(text)
    conflict = conflict_score(text)
    uncertainty = uncertainty_density(text)
    return clamp((reassurance - conflict) - (uncertainty * 0.35), -1.0, 1.0)


def sentiment_score(text: str) -> float:
    return affect_balance_score(text)


def punctuation_features(text: str) -> dict[str, float]:
    value = str(text or "")
    tokens = tokenize(value)
    word_total = max(len(tokens), 1)
    abrupt = 1.0 if len(tokens) <= 2 else 0.0
    repeated = len(PUNCTUATION_REPEAT_RE.findall(value))
    ellipses = len(ELLIPSIS_RE.findall(value))
    caps = len(CAPS_TOKEN_RE.findall(value))
    return {
        "ellipses": float(ellipses),
        "repeated_punctuation": float(repeated),
        "caps_tokens": float(caps),
        "abrupt_reply": abrupt,
        "question_burst": 1.0 if "??" in value else 0.0,
        "exclaim_burst": 1.0 if "!!" in value else 0.0,
        "caps_ratio": caps / word_total,
    }


def punctuation_emphasis_score(text: str) -> float:
    features = punctuation_features(text)
    score = (
        0.3 * features["ellipses"]
        + 0.35 * features["repeated_punctuation"]
        + 0.2 * features["question_burst"]
        + 0.15 * features["caps_tokens"]
    )
    return clamp(score / 3.0, 0.0, 1.0)


def lexical_overlap(a: str, b: str) -> float:
    left = content_tokens(a)
    right = content_tokens(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def responsiveness_score(question_text: str, answer_text: str) -> float:
    overlap = lexical_overlap(question_text, answer_text)
    question_tokens = content_tokens(question_text)
    answer_tokens = content_tokens(answer_text)
    answer_open = 1.0 if str(answer_text).strip().lower().startswith(DIRECT_OPENINGS) else 0.0
    topic_shift_penalty = 0.18 if count_pattern_hits(TOPIC_SHIFT_MARKERS, answer_text) else 0.0
    if not question_tokens or not answer_tokens:
        return clamp(answer_open * 0.25, 0.0, 1.0)
    shared = len(question_tokens & answer_tokens) / max(len(question_tokens), 1)
    score = (0.55 * overlap) + (0.3 * shared) + (0.15 * answer_open) - topic_shift_penalty
    return clamp(score, 0.0, 1.0)


def structure_features(text: str, *, language: str = "en") -> dict[str, float | int | str | bool]:
    value = str(text or "").strip()
    sentence_info = sentence_stats(value, language=language)
    structure = analyze_spacy_structure(value, language=language)
    return {
        **structure,
        "avg_sentence_words": round(float(sentence_info["avg_sentence_words"]), 4),
        "fragment_ratio": round(float(sentence_info["fragment_ratio"]), 4),
    }


def directness_score(
    text: str,
    *,
    question_text: str | None = None,
    language: str = "en",
) -> float:
    lowered = " ".join(str(text or "").strip().lower().split())
    if not lowered:
        return 0.0
    structure = structure_features(lowered, language=language)
    score = 0.18
    if lowered.startswith(DIRECT_OPENINGS):
        score += 0.28
    if any(marker in lowered for marker in EXPLANATION_MARKERS):
        score += 0.14
    if int(structure.get("explanation_clause_count", 0)) > 0:
        score += 0.08
    if any(token in ACTION_VERBS for token in tokenize(lowered)):
        score += 0.12
    if int(structure.get("action_statement_count", 0)) > 0:
        score += 0.1
    if float(structure.get("avg_sentence_words", 0.0)) >= 5.0:
        score += 0.05
    if question_text:
        score += responsiveness_score(question_text, lowered) * 0.24
    score -= hedging_density(lowered) * 1.6
    score -= 0.12 * len(avoidance_markers(lowered))
    score -= 0.08 * len(contradiction_markers(lowered))
    if count_pattern_hits(TOPIC_SHIFT_MARKERS, lowered):
        score -= 0.1
    if float(structure.get("fragment_ratio", 0.0)) >= 0.5:
        score -= 0.08
    if word_count(lowered) <= 2 and not lowered.startswith(DIRECT_OPENINGS):
        score -= 0.08
    return clamp(score, 0.0, 1.0)


def specificity_score(text: str, *, language: str = "en") -> float:
    value = str(text or "")
    tokens = tokenize(value)
    if not tokens:
        return 0.0
    structure = structure_features(value, language=language)
    concrete_time = len(TIME_RE.findall(value))
    day_hits = len(DAY_RE.findall(value))
    action_hits = sum(1 for token in tokens if token in ACTION_VERBS)
    place_hits = sum(1 for token in tokens if token in PLACE_TERMS)
    event_hits = sum(1 for token in tokens if token in EVENT_TERMS)
    causal_hits = sum(1 for marker in EXPLANATION_MARKERS if marker in value.lower())
    number_hits = len(NUMBER_RE.findall(value))
    vague_hits = sum(1 for token in tokens if token in VAGUE_TERMS)
    nounish_hits = max(
        sum(1 for token in tokens if len(token) >= 5 and token not in STOPWORDS),
        int(structure.get("nounish_count", 0)),
    )
    raw = (
        (1.2 * concrete_time)
        + (1.0 * day_hits)
        + (1.0 * max(action_hits, int(structure.get("action_statement_count", 0))))
        + (0.9 * max(place_hits, int(structure.get("place_reference_count", 0))))
        + (0.9 * max(event_hits, int(structure.get("event_reference_count", 0))))
        + (0.95 * max(causal_hits, int(structure.get("explanation_clause_count", 0))))
        + (0.9 * int(structure.get("time_reference_count", 0)))
        + (0.7 * number_hits)
        + (0.18 * nounish_hits)
        - (1.2 * vague_hits)
    ) / max(len(tokens) / 6.0, 1.0)
    if float(structure.get("avg_sentence_words", 0.0)) >= 6.0:
        raw += 0.25
    if int(structure.get("sentence_count", 0)) >= 2 and float(structure.get("fragment_ratio", 0.0)) < 0.5:
        raw += 0.18
    return clamp(raw / 3.4, 0.0, 1.0)


def normalize_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, message in enumerate(messages, start=1):
        if not isinstance(message, dict):
            continue
        text = str(message.get("analysis_text") or message.get("text", "")).strip()
        if not text:
            continue
        normalized.append(
            {
                "message_id": int(message.get("message_id", index)),
                "speaker": str(message.get("speaker", "unknown")).strip() or "unknown",
                "speaker_key": str(message.get("speaker_key", message.get("speaker", "unknown"))),
                "timestamp": message.get("timestamp"),
                "text": text,
                "original_text": str(message.get("text", "")).strip(),
                "is_system": bool(message.get("is_system", False)),
                "message_type": str(message.get("message_type", "text")),
                "analysis_included": bool(message.get("analysis_included", True)),
                "start": float(message.get("start", 0.0) or 0.0),
                "end": float(message.get("end", 0.0) or 0.0),
            }
        )
    return normalized


def parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def pacing_value(items: list[dict[str, Any]]) -> float:
    if not items:
        return 0.0
    timestamps = [parse_timestamp(item.get("timestamp") or item.get("start_timestamp")) for item in items]
    gaps: list[float] = []
    for prev, curr in zip(timestamps, timestamps[1:]):
        if prev is not None and curr is not None:
            gap = (curr - prev).total_seconds()
            if gap >= 0:
                gaps.append(gap)
    if gaps:
        return average(gaps)
    durations = [
        max(float(item.get("end", 0.0) or item.get("end_timestamp", 0.0) or 0.0) - float(item.get("start", 0.0) or item.get("start_timestamp", 0.0) or 0.0), 0.0)
        for item in items
    ]
    durations = [value for value in durations if value > 0.0]
    return average(durations)


def split_windows(items: list[dict[str, Any]], parts: int | None = None) -> list[dict[str, Any]]:
    if not items:
        return []
    count = parts or (4 if len(items) >= 12 else 3 if len(items) >= 6 else 2)
    size = max(1, math.ceil(len(items) / count))
    labels = ["early", "early_middle", "late_middle", "late"]
    windows: list[dict[str, Any]] = []
    for start in range(0, len(items), size):
        chunk = items[start : start + size]
        label_index = min(len(windows), len(labels) - 1)
        first = chunk[0]
        last = chunk[-1]
        windows.append(
            {
                "label": labels[label_index],
                "start_index": start,
                "end_index": start + len(chunk) - 1,
                "start_turn_id": first.get("turn_id", first.get("message_id", start + 1)),
                "end_turn_id": last.get("turn_id", last.get("message_id", start + len(chunk))),
                "items": chunk,
            }
        )
    return windows


def build_question_answer_pairs(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from ..ingest.segmentation import group_turns, link_response_pairs

    turns = group_turns(normalize_messages(messages))
    return link_response_pairs(turns)


def _item_text(item: dict[str, Any]) -> str:
    return str(item.get("text") or item.get("analysis_text") or "").strip()


def _item_latency(item: dict[str, Any]) -> float | None:
    value = item.get("reply_latency_seconds")
    if value is None:
        return None
    return float(value)


def window_metrics(items: list[dict[str, Any]]) -> dict[str, float]:
    usable = [item for item in items if item.get("analysis_included", True) and not item.get("is_system", False)]
    if not usable:
        return {
            "affect_balance": 0.0,
            "uncertainty": 0.0,
            "reassurance": 0.0,
            "conflict": 0.0,
            "directness": 0.0,
            "specificity": 0.0,
            "hedging": 0.0,
            "reply_length": 0.0,
            "response_latency": 0.0,
            "punctuation_emphasis": 0.0,
        }
    texts = [_item_text(item) for item in usable]
    latencies = [value for value in (_item_latency(item) for item in usable) if value is not None]
    return {
        "affect_balance": average([affect_balance_score(text) for text in texts]),
        "uncertainty": average([uncertainty_density(text) for text in texts]),
        "reassurance": average([reassurance_score(text) for text in texts]),
        "conflict": average([conflict_score(text) for text in texts]),
        "directness": average([directness_score(text) for text in texts]),
        "specificity": average([specificity_score(text) for text in texts]),
        "hedging": average([hedging_density(text) for text in texts]),
        "reply_length": average([word_count(text) for text in texts]),
        "response_latency": average(latencies),
        "punctuation_emphasis": average([punctuation_emphasis_score(text) for text in texts]),
    }


def signal_summary(signal: str, delta: float) -> str:
    higher = delta > 0
    mapping = {
        "affect_balance": (
            "Later wording carries more reassurance than earlier wording.",
            "Later wording carries less reassurance and more friction than earlier wording.",
        ),
        "uncertainty": (
            "Later replies use more uncertainty markers.",
            "Later replies use fewer uncertainty markers.",
        ),
        "reassurance": (
            "Later replies include more reassurance language.",
            "Later replies include less reassurance language.",
        ),
        "conflict": (
            "Later replies contain more friction markers.",
            "Later replies contain fewer friction markers.",
        ),
        "directness": (
            "Later replies look more direct.",
            "Later replies look less direct.",
        ),
        "specificity": (
            "Later replies look more detailed.",
            "Later replies look less detailed.",
        ),
        "hedging": (
            "Later replies use more softening language.",
            "Later replies use less softening language.",
        ),
        "reply_length": (
            "Later replies are longer.",
            "Later replies are shorter.",
        ),
        "response_latency": (
            "Response timing becomes slower.",
            "Response timing becomes faster.",
        ),
        "punctuation_emphasis": (
            "Later replies use more punctuation emphasis.",
            "Later replies use less punctuation emphasis.",
        ),
    }
    positive, negative = mapping.get(signal, ("Later responses shift upward.", "Later responses shift downward."))
    return positive if higher else negative


def compute_boundary_events(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for previous, current in zip(windows, windows[1:]):
        deltas: list[dict[str, Any]] = []
        weighted = 0.0
        for signal, weight in WINDOW_SIGNAL_WEIGHTS.items():
            delta = current["metrics"][signal] - previous["metrics"][signal]
            magnitude = abs(delta)
            deltas.append(
                {
                    "signal": signal,
                    "delta": round(delta, 4),
                    "magnitude": round(magnitude, 4),
                    "summary": signal_summary(signal, delta),
                }
            )
            scale = 10.0 if signal == "reply_length" else 600.0 if signal == "response_latency" else 1.0
            weighted += min(magnitude / scale, 1.0) * weight
        ranked = sorted(deltas, key=lambda item: item["magnitude"], reverse=True)
        event = {
            "from": previous["label"],
            "to": current["label"],
            "start_turn_id": previous["start_turn_id"],
            "end_turn_id": current["end_turn_id"],
            "change_starts_at_turn_id": current["start_turn_id"],
            "window_range": [current["start_index"] + 1, current["end_index"] + 1],
            "shift_value": round(weighted, 4),
            "top_signals": ranked[:3],
            "summary": " ".join(item["summary"] for item in ranked[:2]).strip(),
        }
        events.append(event)
    return events
