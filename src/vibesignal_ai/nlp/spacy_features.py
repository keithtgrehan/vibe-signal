"""Optional spaCy-backed structure helpers for deterministic heuristics."""

from __future__ import annotations

from functools import lru_cache
import re

try:  # pragma: no cover - optional dependency
    import spacy
except Exception:  # pragma: no cover - optional dependency
    spacy = None

from .sentence_split import sentence_stats, split_sentences

HAS_SPACY = spacy is not None

_ACTION_HINTS = {"go", "meet", "call", "text", "leave", "arrive", "send", "bring", "pick", "finish", "start", "plan"}
_PLACE_HINTS = {"home", "office", "work", "restaurant", "station", "airport", "school", "gym", "house", "hotel"}
_EVENT_HINTS = {"dinner", "meeting", "trip", "flight", "interview", "call", "appointment", "date", "plan", "weekend"}
_EXPLANATION_RE = re.compile(r"\b(because|since|so that|the reason|which means)\b", re.IGNORECASE)
_SELF_CORRECTION_RE = re.compile(r"\b(i mean|sorry|rather|let me rephrase|what i meant)\b", re.IGNORECASE)
_RESTART_RE = re.compile(r"\b(um|uh|well|so)\b[\s,]+(?:um|uh|well|so)\b", re.IGNORECASE)
_TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3])(?::[0-5]\d)?\s?(?:am|pm)?\b", re.IGNORECASE)
_WORD_RE = re.compile(r"[A-Za-z0-9']+")
_STOPWORDS = {
    "the", "a", "an", "is", "are", "to", "and", "or", "i", "you", "we", "it",
    "of", "in", "on", "for", "this", "that", "be", "with", "at", "my", "your",
}


@lru_cache(maxsize=2)
def _load_spacy_pipeline(language: str = "en"):
    if not HAS_SPACY:
        return None, "unavailable", False
    model_name = "en_core_web_sm" if (language or "en").startswith("en") else None
    if model_name:
        try:
            nlp = spacy.load(model_name, disable=["textcat"])
            if "sentencizer" not in nlp.pipe_names and "parser" not in nlp.pipe_names:
                nlp.add_pipe("sentencizer")
            return nlp, model_name, True
        except Exception:
            pass
    try:
        nlp = spacy.blank("en" if (language or "en").startswith("en") else "xx")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp, "blank_sentencizer", False
    except Exception:
        return None, "unavailable", False


def spacy_backend_name(language: str = "en") -> str:
    _, backend, _ = _load_spacy_pipeline(language)
    return backend


@lru_cache(maxsize=512)
def analyze_spacy_structure(text: str, language: str = "en") -> dict[str, float | int | str | bool]:
    value = str(text or "").strip()
    sentence_info = sentence_stats(value, language=language)
    sentences = split_sentences(value, language=language)
    if not value:
        return {
            "backend": spacy_backend_name(language),
            "syntax_enabled": False,
            "sentence_count": 0,
            "fragment_count": 0,
            "explanation_clause_count": 0,
            "action_statement_count": 0,
            "time_reference_count": 0,
            "place_reference_count": 0,
            "event_reference_count": 0,
            "concrete_reference_count": 0,
            "nounish_count": 0,
            "self_correction_marker_count": 0,
            "restart_marker_count": 0,
        }

    nlp, backend, syntax_enabled = _load_spacy_pipeline(language)
    tokens = [token.lower() for token in _WORD_RE.findall(value)]
    time_refs = len(_TIME_RE.findall(value))
    place_refs = sum(1 for token in tokens if token in _PLACE_HINTS)
    event_refs = sum(1 for token in tokens if token in _EVENT_HINTS)
    explanation_hits = len(_EXPLANATION_RE.findall(value))
    self_correction_hits = len(_SELF_CORRECTION_RE.findall(value))
    restart_hits = len(_RESTART_RE.findall(value))
    action_hits = 0
    nounish_count = sum(1 for token in tokens if len(token) >= 5 and token not in _STOPWORDS)

    if nlp is not None:
        try:
            doc = nlp(value)
            if syntax_enabled:
                action_hits = sum(
                    1
                    for token in doc
                    if token.pos_ in {"VERB", "AUX"} and token.lemma_.lower() in _ACTION_HINTS
                )
                nounish_count = sum(1 for token in doc if token.pos_ in {"NOUN", "PROPN"})
                explanation_hits = max(
                    explanation_hits,
                    sum(
                        1
                        for token in doc
                        if token.dep_ == "mark" and token.text.lower() in {"because", "since"}
                    ),
                )
                time_refs = max(
                    time_refs,
                    sum(1 for ent in doc.ents if ent.label_ in {"DATE", "TIME"}),
                )
                place_refs = max(
                    place_refs,
                    sum(1 for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC"}),
                )
                event_refs = max(
                    event_refs,
                    sum(1 for ent in doc.ents if ent.label_ == "EVENT"),
                )
            else:
                action_hits = sum(1 for token in tokens if token in _ACTION_HINTS)
        except Exception:  # pragma: no cover - environment specific
            action_hits = sum(1 for token in tokens if token in _ACTION_HINTS)
    else:
        action_hits = sum(1 for token in tokens if token in _ACTION_HINTS)

    return {
        "backend": backend,
        "syntax_enabled": syntax_enabled,
        "sentence_count": int(sentence_info["sentence_count"]),
        "fragment_count": int(round(float(sentence_info["fragment_ratio"]) * max(int(sentence_info["sentence_count"]), 1))),
        "explanation_clause_count": explanation_hits,
        "action_statement_count": min(action_hits, max(len(sentences), 1)),
        "time_reference_count": time_refs,
        "place_reference_count": place_refs,
        "event_reference_count": event_refs,
        "concrete_reference_count": time_refs + place_refs + event_refs,
        "nounish_count": nounish_count,
        "self_correction_marker_count": self_correction_hits,
        "restart_marker_count": restart_hits,
    }
