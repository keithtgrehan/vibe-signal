"""Lightweight NLP helpers for deterministic text structure support."""

from .contradiction_adapter import score_statement_relation
from .sentence_split import sentence_stats, split_sentences
from .spacy_features import analyze_spacy_structure, spacy_backend_name

__all__ = [
    "analyze_spacy_structure",
    "score_statement_relation",
    "sentence_stats",
    "split_sentences",
    "spacy_backend_name",
]
