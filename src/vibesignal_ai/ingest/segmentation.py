"""Deterministic turn grouping, response linking, and topical block detection."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from ..features.shared import content_tokens, lexical_overlap, parse_timestamp, safe_excerpt
from ..nlp.sentence_split import sentence_stats


def _seconds_between(left: str | None, right: str | None) -> float | None:
    left_dt = parse_timestamp(left)
    right_dt = parse_timestamp(right)
    if left_dt is None or right_dt is None:
        return None
    return max((right_dt - left_dt).total_seconds(), 0.0)


def group_turns(messages: list[dict[str, Any]], *, max_gap_seconds: float = 900.0) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for message in messages:
        if bool(message.get("is_system")):
            continue
        speaker = str(message.get("speaker", "unknown"))
        timestamp = message.get("timestamp")
        if current is None:
            current = {
                "turn_id": 1,
                "speaker": speaker,
                "speaker_key": message.get("speaker_key", speaker),
                "message_ids": [message["message_id"]],
                "messages": [message],
                "message_types": [message.get("message_type", "text")],
                "start_timestamp": timestamp,
                "end_timestamp": timestamp,
            }
            continue

        gap_seconds = _seconds_between(current.get("end_timestamp"), timestamp)
        can_merge = (
            current["speaker"] == speaker
            and (gap_seconds is None or gap_seconds <= max_gap_seconds)
        )
        if can_merge:
            current["message_ids"].append(message["message_id"])
            current["messages"].append(message)
            current["message_types"].append(message.get("message_type", "text"))
            current["end_timestamp"] = timestamp or current["end_timestamp"]
            continue

        turns.append(_finalize_turn(current, turns[-1] if turns else None))
        current = {
            "turn_id": len(turns) + 1,
            "speaker": speaker,
            "speaker_key": message.get("speaker_key", speaker),
            "message_ids": [message["message_id"]],
            "messages": [message],
            "message_types": [message.get("message_type", "text")],
            "start_timestamp": timestamp,
            "end_timestamp": timestamp,
        }

    if current is not None:
        turns.append(_finalize_turn(current, turns[-1] if turns else None))
    return turns


def _finalize_turn(turn: dict[str, Any], previous_turn: dict[str, Any] | None) -> dict[str, Any]:
    texts = [str(item.get("analysis_text") or item.get("text") or "").strip() for item in turn["messages"]]
    original_texts = [str(item.get("text", "")).strip() for item in turn["messages"]]
    text = "\n".join([value for value in texts if value]).strip()
    original_text = "\n".join([value for value in original_texts if value]).strip()
    sentence_info = sentence_stats(text)
    response_latency = None
    if previous_turn is not None and previous_turn.get("speaker") != turn["speaker"]:
        response_latency = _seconds_between(previous_turn.get("end_timestamp"), turn.get("start_timestamp"))
    return {
        "turn_id": turn["turn_id"],
        "speaker": turn["speaker"],
        "speaker_key": turn.get("speaker_key", turn["speaker"]),
        "message_ids": turn["message_ids"],
        "message_count": len(turn["message_ids"]),
        "message_types": sorted(set(turn["message_types"])),
        "text": text,
        "original_text": original_text,
        "analysis_included": any(item.get("analysis_included") for item in turn["messages"]),
        "timestamp": turn.get("start_timestamp"),
        "start_timestamp": turn.get("start_timestamp"),
        "end_timestamp": turn.get("end_timestamp"),
        "reply_latency_seconds": response_latency,
        "question_like": "?" in original_text or text.lower().startswith(("why", "what", "when", "how", "can you", "could you", "did you", "are you")),
        "word_count": sum(int(item.get("word_count", 0)) for item in turn["messages"]),
        "sentence_count": int(sentence_info["sentence_count"]),
        "avg_sentence_words": round(float(sentence_info["avg_sentence_words"]), 4),
        "fragment_ratio": round(float(sentence_info["fragment_ratio"]), 4),
        "excerpt": safe_excerpt(original_text),
    }


def link_response_pairs(turns: list[dict[str, Any]], *, max_candidates: int = 4) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for index, turn in enumerate(turns):
        if not turn.get("question_like") or not turn.get("analysis_included"):
            continue
        candidates = [candidate for candidate in turns[index + 1 : index + 1 + max_candidates] if candidate.get("speaker") != turn.get("speaker")]
        if not candidates:
            continue
        best_candidate = None
        best_score = -1.0
        for candidate in candidates:
            overlap = lexical_overlap(turn.get("text", ""), candidate.get("text", ""))
            direct_open = 1.0 if candidate.get("text", "").lower().startswith(("yes", "no", "i ", "we ", "because")) else 0.0
            latency = candidate.get("reply_latency_seconds")
            latency_penalty = min((float(latency) / 900.0), 1.0) if latency is not None else 0.15
            score = (0.45 * overlap) + (0.35 * direct_open) + (0.2 * (1.0 - latency_penalty))
            if score > best_score:
                best_candidate = candidate
                best_score = score
        if best_candidate is None:
            continue
        pairs.append(
            {
                "pair_id": len(pairs) + 1,
                "question_turn_id": turn["turn_id"],
                "answer_turn_id": best_candidate["turn_id"],
                "question_speaker": turn["speaker"],
                "answer_speaker": best_candidate["speaker"],
                "question_excerpt": turn["excerpt"],
                "answer_excerpt": best_candidate["excerpt"],
                "overlap": round(lexical_overlap(turn.get("text", ""), best_candidate.get("text", "")), 4),
                "latency_seconds": best_candidate.get("reply_latency_seconds"),
                "link_score": round(best_score, 4),
            }
        )
    return pairs


def detect_topical_blocks(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    previous_tokens: set[str] = set()
    previous_end = None
    for turn in turns:
        tokens = content_tokens(turn.get("text", ""))
        overlap = len(tokens & previous_tokens) / len(tokens | previous_tokens) if tokens and previous_tokens else 0.0
        gap = _seconds_between(previous_end, turn.get("start_timestamp")) if previous_end else None
        force_new = current is None
        if not force_new:
            if gap is not None and gap >= 1800.0:
                force_new = True
            elif overlap < 0.08 and bool(turn.get("question_like")):
                force_new = True
            elif overlap < 0.05 and gap is not None and gap >= 300.0:
                force_new = True
        if force_new:
            if current is not None:
                blocks.append(_finalize_block(current))
            current = {"block_id": len(blocks) + 1, "turns": [turn]}
        else:
            current["turns"].append(turn)
        previous_tokens = tokens or previous_tokens
        previous_end = turn.get("end_timestamp")
    if current is not None:
        blocks.append(_finalize_block(current))
    return blocks


def _finalize_block(block: dict[str, Any]) -> dict[str, Any]:
    turns = block["turns"]
    token_counter: Counter[str] = Counter()
    for turn in turns:
        token_counter.update(content_tokens(turn.get("text", "")))
    return {
        "block_id": block["block_id"],
        "turn_ids": [turn["turn_id"] for turn in turns],
        "start_turn_id": turns[0]["turn_id"],
        "end_turn_id": turns[-1]["turn_id"],
        "dominant_tokens": [token for token, _ in token_counter.most_common(6)],
        "question_turn_count": sum(1 for turn in turns if turn.get("question_like")),
        "speaker_count": len({turn.get("speaker") for turn in turns}),
    }
