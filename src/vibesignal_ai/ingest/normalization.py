"""Deterministic normalization helpers for speakers, text, and language hints."""

from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
import re
from typing import Any
import unicodedata

from ..nlp.sentence_split import sentence_stats, split_sentences

try:  # pragma: no cover - optional dependency
    import emoji as emoji_lib
except Exception:  # pragma: no cover - optional dependency
    emoji_lib = None

try:  # pragma: no cover - optional dependency
    from langdetect import DetectorFactory, LangDetectException, detect
    DetectorFactory.seed = 0
except Exception:  # pragma: no cover - optional dependency
    DetectorFactory = None
    LangDetectException = Exception
    detect = None

try:  # pragma: no cover - optional dependency
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover - optional dependency
    fuzz = None

_SPACE_RE = re.compile(r"\s+")
_NON_WORD_RE = re.compile(r"[^a-z0-9 ]+")
_WORD_RE = re.compile(r"[a-z0-9']+")
_SHORTHAND_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bidk\b", re.IGNORECASE), "i do not know"),
    (re.compile(r"\bimo\b", re.IGNORECASE), "in my opinion"),
    (re.compile(r"\btbh\b", re.IGNORECASE), "to be honest"),
    (re.compile(r"\bbrb\b", re.IGNORECASE), "be right back"),
    (re.compile(r"\bomw\b", re.IGNORECASE), "on my way"),
    (re.compile(r"\bttyl\b", re.IGNORECASE), "talk to you later"),
    (re.compile(r"\bu\b", re.IGNORECASE), "you"),
    (re.compile(r"\bur\b", re.IGNORECASE), "your"),
)

_PLACEHOLDER_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("image_omitted", re.compile(r"(image omitted|photo omitted|<media omitted>)", re.IGNORECASE)),
    ("video_omitted", re.compile(r"(video omitted|gif omitted)", re.IGNORECASE)),
    ("audio_omitted", re.compile(r"(audio omitted|voice message omitted|ptt omitted)", re.IGNORECASE)),
    ("document_omitted", re.compile(r"(document omitted|sticker omitted|contact card omitted)", re.IGNORECASE)),
    ("deleted_message", re.compile(r"(message deleted|you deleted this message|this message was deleted)", re.IGNORECASE)),
)
_SYSTEM_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"messages to this chat are now secured", re.IGNORECASE),
    re.compile(r"changed the subject", re.IGNORECASE),
    re.compile(r"changed this group's icon", re.IGNORECASE),
    re.compile(r"joined using this group's invite link", re.IGNORECASE),
    re.compile(r"missed (voice|video) call", re.IGNORECASE),
    re.compile(r"created group", re.IGNORECASE),
)


def normalize_whitespace(text: str) -> str:
    return _SPACE_RE.sub(" ", str(text or "").strip())


def normalize_speaker_key(name: str) -> str:
    lowered = normalize_whitespace(name).lower()
    lowered = _NON_WORD_RE.sub(" ", lowered)
    return normalize_whitespace(lowered)


def speaker_alias_map(names: list[str]) -> dict[str, str]:
    unique = [name for name in names if normalize_speaker_key(name)]
    alias_map: dict[str, str] = {}
    canonicals: list[str] = []
    for name in unique:
        key = normalize_speaker_key(name)
        if not key:
            continue
        chosen = None
        for canonical in canonicals:
            canonical_key = normalize_speaker_key(canonical)
            if key == canonical_key:
                chosen = canonical
                break
            if key.split()[:1] != canonical_key.split()[:1]:
                continue
            similarity = (
                float(fuzz.ratio(key, canonical_key))
                if fuzz is not None
                else SequenceMatcher(None, key, canonical_key).ratio() * 100.0
            )
            if similarity >= 95 and abs(len(key) - len(canonical_key)) <= 3:
                chosen = canonical
                break
        if chosen is None:
            canonicals.append(name)
            chosen = name
        alias_map[name] = chosen
    return alias_map


def normalize_speakers(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    names = [str(item.get("speaker", "")).strip() for item in messages if not item.get("is_system")]
    alias_map = speaker_alias_map(names)
    normalized: list[dict[str, Any]] = []
    canonical_counts = Counter(alias_map.values())
    for item in messages:
        row = dict(item)
        original = str(row.get("speaker", "")).strip() or "unknown"
        canonical = alias_map.get(original, original)
        row["speaker_original"] = original
        row["speaker"] = canonical
        row["speaker_key"] = normalize_speaker_key(canonical) or "unknown"
        row["speaker_alias_confidence"] = "exact" if original == canonical else "fuzzy"
        row["speaker_alias_group_size"] = canonical_counts.get(canonical, 1)
        normalized.append(row)
    return normalized


def classify_message_text(text: str, *, is_system: bool = False) -> str:
    value = normalize_whitespace(text)
    if is_system:
        return "system_notice"
    for label, pattern in _PLACEHOLDER_PATTERNS:
        if pattern.search(value):
            return label
    for pattern in _SYSTEM_PATTERNS:
        if pattern.search(value):
            return "system_notice"
    return "text"


def normalize_emojis(text: str) -> str:
    value = str(text or "")
    if emoji_lib is None:
        normalized_parts: list[str] = []
        for character in value:
            if character.isspace():
                normalized_parts.append(" ")
                continue
            category = unicodedata.category(character)
            name = unicodedata.name(character, "")
            if name and category == "So" and not character.isascii():
                normalized_parts.append(f" {name.lower().replace(' ', '_')} ")
            else:
                normalized_parts.append(character)
        return normalize_whitespace("".join(normalized_parts))
    demojized = emoji_lib.demojize(value, delimiters=(" ", " "))
    demojized = demojized.replace(":", " ")
    return normalize_whitespace(demojized)


def normalize_shorthand(text: str) -> str:
    value = str(text or "")
    for pattern, replacement in _SHORTHAND_PATTERNS:
        value = pattern.sub(replacement, value)
    return normalize_whitespace(value)


def build_analysis_text(text: str) -> str:
    return normalize_shorthand(normalize_emojis(text))


def detect_language_hint(text: str, *, default: str = "unknown") -> str:
    value = normalize_whitespace(text)
    if len(value) < 12 or len(_WORD_RE.findall(value.lower())) < 3:
        return default
    if detect is None:
        ascii_letters = sum(1 for char in value if char.isascii() and char.isalpha())
        if ascii_letters / max(len(value), 1) > 0.6:
            return "en"
        return default
    try:
        return str(detect(value)).lower()
    except LangDetectException:
        return default


def detect_conversation_language(messages: list[dict[str, Any]], *, fallback: str = "unknown") -> str:
    samples = [
        str(item.get("analysis_text") or item.get("text") or "")
        for item in messages
        if item.get("message_type") == "text" and not item.get("is_system")
    ]
    combined = " ".join(samples[:50])
    return detect_language_hint(combined, default=fallback)


def enrich_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = normalize_speakers(messages)
    enriched: list[dict[str, Any]] = []
    for item in normalized:
        row = dict(item)
        original_text = str(row.get("text", "")).strip()
        row["original_text"] = original_text
        row["emoji_text"] = normalize_emojis(original_text)
        row["normalized_text"] = normalize_shorthand(original_text)
        row["analysis_text"] = build_analysis_text(original_text)
        row["message_type"] = classify_message_text(original_text, is_system=bool(row.get("is_system")))
        row["analysis_included"] = row["message_type"] == "text"
        row["detected_language"] = detect_language_hint(row["analysis_text"])
        sentence_language = row["detected_language"] if row["detected_language"] != "unknown" else "en"
        sentences = split_sentences(row["analysis_text"], language=sentence_language)
        sentence_info = sentence_stats(row["analysis_text"], language=sentence_language)
        row["word_count"] = len(_WORD_RE.findall(row["analysis_text"].lower()))
        row["char_count"] = len(original_text)
        row["analysis_sentences"] = sentences
        row["sentence_count"] = int(sentence_info["sentence_count"])
        row["avg_sentence_words"] = round(float(sentence_info["avg_sentence_words"]), 4)
        row["fragment_ratio"] = round(float(sentence_info["fragment_ratio"]), 4)
        enriched.append(row)

    conversation_language = detect_conversation_language(enriched)
    for row in enriched:
        row["conversation_detected_language"] = conversation_language
    return enriched
