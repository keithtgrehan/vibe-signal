"""Sentence splitting helpers with pySBD, spaCy, and regex fallbacks."""

from __future__ import annotations

from functools import lru_cache
import re

try:  # pragma: no cover - optional dependency
    import pysbd
except Exception:  # pragma: no cover - optional dependency
    pysbd = None

try:  # pragma: no cover - optional dependency
    import spacy
except Exception:  # pragma: no cover - optional dependency
    spacy = None

HAS_PYSBD = pysbd is not None
HAS_SPACY = spacy is not None

_LINE_BREAK_RE = re.compile(r"(?:\r?\n)+")
_REGEX_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _clean_sentences(parts: list[str]) -> list[str]:
    cleaned = [" ".join(str(part or "").split()).strip() for part in parts]
    return [part for part in cleaned if part]


@lru_cache(maxsize=4)
def _get_pysbd_segmenter(language: str = "en"):
    if not HAS_PYSBD:
        return None
    try:
        return pysbd.Segmenter(language=(language or "en").split("-")[0], clean=False)
    except Exception:  # pragma: no cover - environment specific
        return None


@lru_cache(maxsize=4)
def _get_spacy_sentencizer(language: str = "en"):
    if not HAS_SPACY:
        return None
    try:
        nlp = spacy.blank("en" if (language or "en").startswith("en") else "xx")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp
    except Exception:  # pragma: no cover - environment specific
        return None


def _regex_split(text: str) -> list[str]:
    value = str(text or "").strip()
    if not value:
        return []
    normalized = _LINE_BREAK_RE.sub("\n", value)
    if "\n" in normalized:
        parts: list[str] = []
        for block in normalized.split("\n"):
            parts.extend(_REGEX_SENTENCE_RE.split(block))
        return _clean_sentences(parts)
    return _clean_sentences(_REGEX_SENTENCE_RE.split(normalized))


def split_sentences(
    text: str,
    *,
    language: str = "en",
    backend: str = "auto",
) -> list[str]:
    value = str(text or "").strip()
    if not value:
        return []

    if backend in {"auto", "pysbd"}:
        segmenter = _get_pysbd_segmenter(language)
        if segmenter is not None:
            try:
                sentences = _clean_sentences(list(segmenter.segment(value)))
                if sentences:
                    return sentences
            except Exception:  # pragma: no cover - environment specific
                if backend == "pysbd":
                    return _regex_split(value)

    if backend in {"auto", "spacy"}:
        nlp = _get_spacy_sentencizer(language)
        if nlp is not None:
            try:
                doc = nlp(value)
                sentences = _clean_sentences([sent.text for sent in doc.sents])
                if sentences:
                    return sentences
            except Exception:  # pragma: no cover - environment specific
                if backend == "spacy":
                    return _regex_split(value)

    return _regex_split(value)


def sentence_stats(
    text: str,
    *,
    language: str = "en",
    backend: str = "auto",
) -> dict[str, float | int]:
    sentences = split_sentences(text, language=language, backend=backend)
    if not sentences:
        return {
            "sentence_count": 0,
            "avg_sentence_words": 0.0,
            "fragment_ratio": 0.0,
        }
    word_lengths = [len(sentence.split()) for sentence in sentences]
    fragment_count = sum(
        1
        for sentence in sentences
        if not sentence.endswith((".", "!", "?")) and len(sentence.split()) >= 3
    )
    return {
        "sentence_count": len(sentences),
        "avg_sentence_words": sum(word_lengths) / len(word_lengths),
        "fragment_ratio": fragment_count / len(sentences),
    }
