from __future__ import annotations

from pathlib import Path

from vibesignal_ai.config import runtime_flags
from vibesignal_ai.nlp import sentence_split
from vibesignal_ai.nlp import spacy_features
from vibesignal_ai.pipeline.run import analyze_conversation


def test_sentence_split_regex_backend_and_auto_fallback(monkeypatch) -> None:
    text = "I can make it by 7. I already booked the table.\nCan you meet me there?"

    regex_sentences = sentence_split.split_sentences(text, backend="regex")
    assert len(regex_sentences) == 3

    monkeypatch.setattr(sentence_split, "HAS_PYSBD", False)
    sentence_split._get_pysbd_segmenter.cache_clear()

    auto_sentences = sentence_split.split_sentences(text, backend="auto")
    assert len(auto_sentences) >= 3
    assert "booked the table." in auto_sentences[1]


def test_spacy_structure_fallback_keeps_deterministic_cues(monkeypatch) -> None:
    text = "I can meet you at the station at 7 pm because I already booked the table."
    result = spacy_features.analyze_spacy_structure(text)

    assert result["explanation_clause_count"] >= 1
    assert result["time_reference_count"] >= 1
    assert result["action_statement_count"] >= 1

    monkeypatch.setattr(spacy_features, "HAS_SPACY", False)
    spacy_features._load_spacy_pipeline.cache_clear()
    spacy_features.analyze_spacy_structure.cache_clear()

    fallback = spacy_features.analyze_spacy_structure(
        "I will call you tomorrow because the train arrives late."
    )
    assert fallback["backend"] == "unavailable"
    assert fallback["explanation_clause_count"] >= 1


def test_pipeline_runs_without_optional_nlp_or_vad_modules(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from vibesignal_ai.audio import vad

    fixture = Path(__file__).parent / "fixtures" / "relationship_chat_hardened.txt"

    monkeypatch.setattr(sentence_split, "HAS_PYSBD", False)
    monkeypatch.setattr(sentence_split, "HAS_SPACY", False)
    sentence_split._get_pysbd_segmenter.cache_clear()
    sentence_split._get_spacy_sentencizer.cache_clear()

    monkeypatch.setattr(spacy_features, "HAS_SPACY", False)
    spacy_features._load_spacy_pipeline.cache_clear()
    spacy_features.analyze_spacy_structure.cache_clear()

    monkeypatch.setattr(runtime_flags, "ENABLE_OPENSMILE", False)
    monkeypatch.setattr(runtime_flags, "ENABLE_NLI", False)
    monkeypatch.setattr(runtime_flags, "ENABLE_VAD", False)

    monkeypatch.setattr(vad, "HAS_SILERO_VAD", False)
    vad._load_model.cache_clear()

    result = analyze_conversation(
        input_path=fixture,
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path,
        rights_asserted=True,
    )

    assert Path(result["conversation_root"]).exists()
    assert Path(result["ui_summary_path"]).exists()
