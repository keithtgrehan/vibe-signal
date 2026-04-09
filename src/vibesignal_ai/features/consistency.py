"""Response consistency checks without verdict language."""

from __future__ import annotations

from collections import Counter
from typing import Any

from ..config import runtime_flags
from ..nlp.contradiction_adapter import score_statement_relation
from .shared import (
    avoidance_markers,
    clamp,
    contradiction_markers,
    directness_score,
    responsiveness_score,
    safe_excerpt,
    specificity_score,
    stddev,
)


def analyze_consistency(
    messages: list[dict[str, Any]],
    *,
    turns: list[dict[str, Any]] | None = None,
    response_pairs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from ..ingest.segmentation import group_turns, link_response_pairs
    from .shared import normalize_messages

    normalized = normalize_messages(messages)
    conversation_turns = turns or group_turns(normalized)
    pairs = response_pairs or link_response_pairs(conversation_turns)
    if not pairs:
        return {
            "consistency_level": "insufficient_data",
            "consistency_score": 0.0,
            "top_reasons": ["Not enough question-and-response pairs were found."],
            "supporting_spans": [],
            "consistency_events": [],
            "metrics": {},
        }

    turn_lookup = {turn["turn_id"]: turn for turn in conversation_turns}
    rows: list[dict[str, Any]] = []
    marker_counter: Counter[str] = Counter()
    contradiction_counter: Counter[str] = Counter()
    nli_rows_available = 0
    for pair in pairs:
        question = turn_lookup[pair["question_turn_id"]]
        answer = turn_lookup[pair["answer_turn_id"]]
        overlap = responsiveness_score(question["text"], answer["text"])
        directness = directness_score(answer["text"], question_text=question["text"])
        specificity = specificity_score(answer["text"])
        markers = avoidance_markers(answer["text"])
        reversals = contradiction_markers(answer["text"])
        relation = score_statement_relation(
            question["text"],
            answer["text"],
            enabled=bool(runtime_flags.ENABLE_NLI),
            model_name=runtime_flags.NLI_MODEL_NAME,
        )
        if relation.get("available"):
            nli_rows_available += 1
        for marker in markers:
            marker_counter[marker] += 1
        for marker in reversals:
            contradiction_counter[marker] += 1
        direct_answer = 1.0 if directness >= 0.52 and overlap >= 0.16 and not markers else 0.0
        rows.append(
            {
                "pair_id": pair["pair_id"],
                "question_turn_id": question["turn_id"],
                "answer_turn_id": answer["turn_id"],
                "question_speaker": question["speaker"],
                "answer_speaker": answer["speaker"],
                "direct_answer": direct_answer,
                "responsiveness": round(overlap, 4),
                "directness": round(directness, 4),
                "specificity": round(specificity, 4),
                "avoidance_markers": markers,
                "contradiction_markers": reversals,
                "optional_statement_relation": relation.get("relation", "unavailable"),
                "optional_statement_relation_scores": relation.get("scores", {}),
                "optional_statement_relation_backend": relation.get("backend", "disabled"),
                "latency_seconds": pair.get("latency_seconds"),
                "question_excerpt": safe_excerpt(question["original_text"]),
                "answer_excerpt": safe_excerpt(answer["original_text"]),
            }
        )

    direct_answer_ratio = sum(item["direct_answer"] for item in rows) / len(rows)
    avg_overlap = sum(item["responsiveness"] for item in rows) / len(rows)
    specificity_values = [item["specificity"] for item in rows]
    specificity_consistency = clamp(1.0 - stddev(specificity_values), 0.0, 1.0)
    avoidance_ratio = sum(1 for item in rows if item["avoidance_markers"]) / len(rows)
    contradiction_ratio = sum(1 for item in rows if item["contradiction_markers"]) / len(rows)
    optional_alignment_ratio = (
        sum(1 for item in rows if item["optional_statement_relation"] == "aligned_statement_relation")
        / len(rows)
    )
    optional_contradiction_signal_ratio = (
        sum(1 for item in rows if item["optional_statement_relation"] == "contradiction_signal")
        / len(rows)
    )

    score = (
        0.3 * direct_answer_ratio
        + 0.28 * avg_overlap
        + 0.2 * specificity_consistency
        + 0.12 * (1.0 - avoidance_ratio)
        + 0.1 * (1.0 - contradiction_ratio)
    ) * 100.0
    if nli_rows_available:
        score = clamp(
            (score / 100.0)
            + (0.04 * optional_alignment_ratio)
            - (0.04 * optional_contradiction_signal_ratio),
            0.0,
            1.0,
        ) * 100.0

    if score >= 74.0:
        level = "stable"
    elif score >= 48.0:
        level = "mixed"
    else:
        level = "weakened"

    reasons: list[str] = []
    if direct_answer_ratio < 0.55:
        reasons.append("Direct answer style weakens across the linked response pairs.")
    if avg_overlap < 0.25:
        reasons.append("Responses stay less aligned with the question wording and topic.")
    if avoidance_ratio > 0.25:
        reasons.append("Deflection or non-answer markers appear repeatedly.")
    if specificity_consistency < 0.62:
        reasons.append("Specific detail continuity becomes less steady from one answer to the next.")
    if contradiction_ratio > 0.2:
        reasons.append("Later answers include more reversal-style wording.")
    if nli_rows_available and optional_contradiction_signal_ratio > 0.25:
        reasons.append("Optional local statement-relation support finds more contradiction-style pairings.")
    if not reasons:
        reasons.append("Response style stays relatively aligned and comparably detailed across the sampled pairs.")

    weakest = sorted(
        rows,
        key=lambda item: (
            item["direct_answer"],
            item["responsiveness"],
            item["specificity"],
            -len(item["avoidance_markers"]),
        ),
    )[:4]
    consistency_events = [
        {
            "pair_id": item["pair_id"],
            "question_turn_id": item["question_turn_id"],
            "answer_turn_id": item["answer_turn_id"],
            "event_type": "reduced_alignment" if item["responsiveness"] < 0.22 else "reduced_specificity",
            "summary": (
                "The answer tracks the question less closely and uses a softer answer style."
                if item["responsiveness"] < 0.22
                else "The answer stays comparatively less detailed than stronger earlier answers."
            ),
            "responsiveness": item["responsiveness"],
            "directness": item["directness"],
            "specificity": item["specificity"],
            "avoidance_markers": ", ".join(item["avoidance_markers"]),
            "contradiction_markers": ", ".join(item["contradiction_markers"]),
            "optional_statement_relation": item["optional_statement_relation"],
            "question_excerpt": item["question_excerpt"],
            "answer_excerpt": item["answer_excerpt"],
        }
        for item in weakest
    ]

    repeated_patterns = [marker for marker, count in marker_counter.items() if count >= 2]
    repeated_reversals = [marker for marker, count in contradiction_counter.items() if count >= 2]

    return {
        "consistency_level": level,
        "consistency_score": round(score, 2),
        "top_reasons": reasons,
        "supporting_spans": weakest,
        "consistency_events": consistency_events,
        "metrics": {
            "direct_answer_ratio": round(direct_answer_ratio, 4),
            "question_answer_overlap": round(avg_overlap, 4),
            "avoidance_ratio": round(avoidance_ratio, 4),
            "contradiction_ratio": round(contradiction_ratio, 4),
            "specificity_consistency": round(specificity_consistency, 4),
            "repeated_non_answer_patterns": repeated_patterns,
            "repeated_reversal_patterns": repeated_reversals,
            "optional_nli": {
                "enabled": bool(runtime_flags.ENABLE_NLI),
                "available_pair_count": nli_rows_available,
                "alignment_ratio": round(optional_alignment_ratio, 4),
                "contradiction_signal_ratio": round(optional_contradiction_signal_ratio, 4),
                "model_name": runtime_flags.NLI_MODEL_NAME,
            },
        },
    }
