#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_ROOT = REPO_ROOT / "data" / "restricted" / "private_whatsapp"
DEFAULT_MESSAGES = RESTRICTED_ROOT / "processed" / "private_messages_redacted.jsonl"
DEFAULT_OUTPUT_DIR = RESTRICTED_ROOT / "reports"
REPORT_MD = "whatsapp_dynamics_report.md"
REPORT_JSON = "whatsapp_dynamics_report.json"
ASK_WINDOW_SECONDS = 48 * 60 * 60
FAST_RESPONSE_SECONDS = 10 * 60

ROLE_SELF = {"self", "me", "user", "owner"}
ROLE_OTHER = {"other", "them", "partner", "contact"}
WORD_RE = re.compile(r"[A-Za-z0-9']+")
DIRECT_ASK_RE = re.compile(
    r"\?|"
    r"\b(?:can|could|would|will|did|do|are|is|when|what|where|why|how)\s+(?:you|we|i)\b|"
    r"\b(?:please|confirm|send|answer|reply|explain|share|review|check)\b",
    re.IGNORECASE,
)
UNCLEAR_TIMING_RE = re.compile(
    r"\b(?:maybe|later|sometime|soon|eventually|not sure|unclear|we'?ll see|when you can|another time|tbd|no idea)\b",
    re.IGNORECASE,
)
PRESSURE_URGENCY_RE = re.compile(
    r"\b(?:right now|asap|urgent|immediately|you have to|you must|must|deadline|no choice|owe me|or else|"
    r"answer now|reply now|by tonight|by today|prove it)\b",
    re.IGNORECASE,
)
PRESSURE_REDUCER_RE = re.compile(r"\b(?:no pressure|no rush|no stress|when you can|only if you can)\b", re.IGNORECASE)
REPAIR_REASSURANCE_RE = re.compile(
    r"\b(?:sorry|apologize|apology|rephrase|reset|repair|clarify|all good|no worries|no pressure|"
    r"no rush|no stress|thanks for clarifying|appreciate|that helps|we can talk)\b",
    re.IGNORECASE,
)
BOUNDARY_RE = re.compile(
    r"\b(?:i cannot|i can'?t|i do not want|i don'?t want|not comfortable|not available|need space|"
    r"no,|no\.|boundary|do not share|cannot share|can't share)\b",
    re.IGNORECASE,
)
BLOCKED_REPORT_RE = re.compile(
    r"\b(?:clinical|relationship score|hidden intent|secret intent|hidden stressor|hiding anger|suppressed emotion|"
    r"they are lying|they are manipulating|attachment style|neurotype|deception|cheating detector|"
    r"manipulat(?:e|ion|ive))\b",
    re.IGNORECASE,
)
AUDIO_COLUMNS = {
    "audio_id",
    "message_id",
    "speaker_role",
    "timestamp",
    "pitch_mean",
    "pitch_std",
    "energy_mean",
    "voice_break_rate",
    "pause_rate",
    "wav2vec_cluster",
    "valence_proxy",
    "arousal_proxy",
    "dominance_proxy",
}


@dataclass(frozen=True)
class Message:
    role: str
    timestamp: datetime | None
    text: str
    message_id: str


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def _is_under(path: Path, root: Path) -> bool:
    try:
        _resolve(path).relative_to(_resolve(root))
        return True
    except ValueError:
        return False


def _safe_error(message: str) -> None:
    print(message, file=sys.stderr)


def _normalize_role(value: Any) -> str:
    lowered = str(value or "").strip().lower()
    if lowered in ROLE_SELF or lowered.startswith("self"):
        return "self"
    if lowered in ROLE_OTHER or lowered.startswith("other"):
        return "other"
    return "other"


def _parse_time(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    candidates = [text]
    if text.endswith("Z"):
        candidates.append(text[:-1] + "+00:00")
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(str(text or "")))


def _message_id(row: dict[str, Any], index: int) -> str:
    for key in ("message_id", "id", "messageId"):
        if row.get(key):
            return str(row[key])
    return f"row_{index}"


def _load_messages(path: Path) -> list[Message]:
    rows: list[Message] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        role = _normalize_role(payload.get("speaker_role", payload.get("role", payload.get("author"))))
        timestamp = _parse_time(payload.get("timestamp", payload.get("created_at", payload.get("date"))))
        rows.append(
            Message(
                role=role,
                timestamp=timestamp,
                text=str(payload.get("text", payload.get("message", "")) or ""),
                message_id=_message_id(payload, index),
            )
        )
    return sorted(rows, key=lambda item: item.timestamp or datetime.max.replace(tzinfo=timezone.utc))


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percentile / 100
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[int(rank)]
    return ordered[lower] * (upper - rank) + ordered[upper] * (rank - lower)


def _summary_distribution(values: list[float]) -> dict[str, float | None]:
    return {
        "count": len(values),
        "p10_seconds": _percentile(values, 10),
        "p25_seconds": _percentile(values, 25),
        "median_seconds": statistics.median(values) if values else None,
        "p75_seconds": _percentile(values, 75),
        "p90_seconds": _percentile(values, 90),
        "max_seconds": max(values) if values else None,
    }


def _cue_flags(text: str) -> dict[str, bool]:
    word_count = _word_count(text)
    pressure = bool(PRESSURE_URGENCY_RE.search(text)) and not bool(PRESSURE_REDUCER_RE.search(text))
    return {
        "direct_ask": bool(DIRECT_ASK_RE.search(text)),
        "unclear_timing": bool(UNCLEAR_TIMING_RE.search(text)),
        "pressure_urgency": pressure,
        "repair_reassurance": bool(REPAIR_REASSURANCE_RE.search(text)),
        "boundary": bool(BOUNDARY_RE.search(text)),
        "low_signal": word_count <= 3,
    }


def _cue_category_counts(messages: list[Message]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for message in messages:
        for cue, present in _cue_flags(message.text).items():
            if present:
                counts[cue] += 1
    return counts


def _latency_events(messages: list[Message]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for previous, current in zip(messages, messages[1:]):
        if previous.role == current.role or previous.timestamp is None or current.timestamp is None:
            continue
        delta = (current.timestamp - previous.timestamp).total_seconds()
        if delta < 0:
            continue
        events.append({"responder": current.role, "from_role": previous.role, "latency_seconds": delta})
    return events


def _run_lengths(messages: list[Message]) -> list[dict[str, int | str]]:
    if not messages:
        return []
    runs: list[dict[str, int | str]] = []
    current_role = messages[0].role
    current_length = 1
    for message in messages[1:]:
        if message.role == current_role:
            current_length += 1
        else:
            runs.append({"role": current_role, "length": current_length})
            current_role = message.role
            current_length = 1
    runs.append({"role": current_role, "length": current_length})
    return runs


def _ask_metrics(messages: list[Message]) -> dict[str, Any]:
    ask_counts: Counter[str] = Counter()
    unanswered_counts: Counter[str] = Counter()
    for index, message in enumerate(messages):
        if not _cue_flags(message.text)["direct_ask"]:
            continue
        ask_counts[message.role] += 1
        answered = False
        for later in messages[index + 1 :]:
            if message.timestamp and later.timestamp:
                delta = (later.timestamp - message.timestamp).total_seconds()
                if delta > ASK_WINDOW_SECONDS:
                    break
            if later.role != message.role:
                answered = True
                break
        if not answered:
            unanswered_counts[message.role] += 1
    return {
        "direct_ask_count_by_role": {role: ask_counts.get(role, 0) for role in ("self", "other")},
        "direct_ask_rate_by_role": {
            role: ask_counts.get(role, 0) / max(1, sum(1 for message in messages if message.role == role)) for role in ("self", "other")
        },
        "unanswered_ask_candidates_by_role": {role: unanswered_counts.get(role, 0) for role in ("self", "other")},
        "unanswered_ask_candidate_rate_by_role": {
            role: unanswered_counts.get(role, 0) / max(1, ask_counts.get(role, 0)) for role in ("self", "other")
        },
        "response_window_seconds": ASK_WINDOW_SECONDS,
    }


def _window_key(timestamp: datetime | None, granularity: str) -> str | None:
    if timestamp is None:
        return None
    if granularity == "day":
        return timestamp.date().isoformat()
    year, week, _ = timestamp.isocalendar()
    return f"{year}-W{week:02d}"


def _ordinal_windows(keys: list[str], prefix: str) -> dict[str, str]:
    return {key: f"{prefix}_{index}" for index, key in enumerate(sorted(set(keys)), start=1)}


def _window_metrics(messages: list[Message], granularity: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[Message]] = defaultdict(list)
    for message in messages:
        key = _window_key(message.timestamp, granularity)
        if key:
            grouped[key].append(message)
    aliases = _ordinal_windows(list(grouped), granularity)
    rows: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for key in sorted(grouped):
        window_messages = grouped[key]
        cue_counts = _cue_category_counts(window_messages)
        message_counts = Counter(message.role for message in window_messages)
        word_counts = Counter()
        for message in window_messages:
            word_counts[message.role] += _word_count(message.text)
        current = {
            "window": aliases[key],
            "message_count_total": len(window_messages),
            "message_counts_by_role": {role: message_counts.get(role, 0) for role in ("self", "other")},
            "word_counts_by_role": {role: word_counts.get(role, 0) for role in ("self", "other")},
            "cue_counts": dict(sorted(cue_counts.items())),
        }
        if previous:
            current["shift_from_previous"] = {
                "message_count_delta": current["message_count_total"] - previous["message_count_total"],
                "pressure_urgency_delta": current["cue_counts"].get("pressure_urgency", 0)
                - previous["cue_counts"].get("pressure_urgency", 0),
                "repair_reassurance_delta": current["cue_counts"].get("repair_reassurance", 0)
                - previous["cue_counts"].get("repair_reassurance", 0),
                "unclear_timing_delta": current["cue_counts"].get("unclear_timing", 0)
                - previous["cue_counts"].get("unclear_timing", 0),
            }
        else:
            current["shift_from_previous"] = None
        rows.append(current)
        previous = current
    return rows


def _message_lookup(messages: list[Message]) -> dict[str, Message]:
    return {message.message_id: message for message in messages}


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_audio(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = AUDIO_COLUMNS - columns
        if missing:
            return [], missing
        return [dict(row) for row in reader], set()


def _audio_row_diverges(row: dict[str, str], message: Message) -> bool:
    cues = _cue_flags(message.text)
    arousal = _float_or_none(row.get("arousal_proxy"))
    valence = _float_or_none(row.get("valence_proxy"))
    if arousal is None:
        return False
    text_high_activation = cues["pressure_urgency"] or cues["boundary"]
    text_low_pressure = cues["repair_reassurance"] and not cues["pressure_urgency"]
    different = (text_high_activation and arousal < 0.4) or (text_low_pressure and arousal > 0.7)
    if valence is not None and cues["repair_reassurance"] and valence < 0.35:
        different = True
    return different


def _audio_summary(path: Path | None, messages: list[Message]) -> dict[str, Any]:
    if path is None:
        return {
            "provided": False,
            "status": "not_provided",
            "safe_summary": "No audio telemetry provided.",
            "feature_divergence": {"count": 0, "rate": 0.0, "safe_language": "No audio telemetry provided."},
        }
    rows, missing = _validate_audio(path)
    if missing:
        raise ValueError("Audio matrix missing required columns: " + ", ".join(sorted(missing)))
    lookup = _message_lookup(messages)
    joined = [row for row in rows if str(row.get("message_id", "")) in lookup]
    by_role: dict[str, dict[str, Any]] = {}
    divergence_count = 0
    for role in ("self", "other"):
        role_rows = [row for row in joined if _normalize_role(row.get("speaker_role")) == role]
        role_divergence = sum(1 for row in role_rows if _audio_row_diverges(row, lookup[str(row.get("message_id", ""))]))
        by_role[role] = {
            "joined_count": len(role_rows),
            "feature_divergence_count": role_divergence,
            "feature_divergence_rate": role_divergence / max(1, len(role_rows)),
        }
    for row in joined:
        message = lookup[str(row.get("message_id", ""))]
        if _audio_row_diverges(row, message):
            divergence_count += 1
    joined_count = len(joined)
    return {
        "provided": True,
        "status": "aggregated",
        "rows_read": len(rows),
        "joined_rows": joined_count,
        "aggregate_by_role": by_role,
        "aggregate_by_time": _audio_time_summary(joined, lookup),
        "feature_divergence": {
            "count": divergence_count,
            "rate": divergence_count / max(1, joined_count),
            "safe_language": "text and audio features point in different directions",
        },
        "safe_summary": "Audio telemetry was aggregated by role and time. Feature divergence is not an emotion claim.",
    }


def _audio_time_summary(rows: list[dict[str, str]], lookup: dict[str, Message]) -> dict[str, list[dict[str, Any]]]:
    summary: dict[str, list[dict[str, Any]]] = {}
    for granularity in ("day", "week"):
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            timestamp = _parse_time(row.get("timestamp"))
            if timestamp is None and str(row.get("message_id", "")) in lookup:
                timestamp = lookup[str(row.get("message_id", ""))].timestamp
            key = _window_key(timestamp, granularity)
            if key:
                grouped[key].append(row)
        aliases = _ordinal_windows(list(grouped), granularity)
        summary[granularity] = []
        for key in sorted(grouped):
            window_rows = grouped[key]
            by_role_counts = Counter(_normalize_role(row.get("speaker_role")) for row in window_rows)
            divergence_count = sum(1 for row in window_rows if _audio_row_diverges(row, lookup[str(row.get("message_id", ""))]))
            item: dict[str, Any] = {
                "window": aliases[key],
                "joined_count": len(window_rows),
                "counts_by_role": {role: by_role_counts.get(role, 0) for role in ("self", "other")},
                "feature_divergence_count": divergence_count,
                "feature_divergence_rate": divergence_count / max(1, len(window_rows)),
            }
            summary[granularity].append(item)
    return summary


def _low_signal_warnings(messages: list[Message], audio: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if len(messages) < 10:
        warnings.append("Low-confidence signal: fewer than 10 messages were available.")
    if any(message.timestamp is None for message in messages):
        warnings.append("Low-confidence signal: one or more messages lacked parseable timestamps.")
    counts = Counter(message.role for message in messages)
    if counts.get("self", 0) == 0 or counts.get("other", 0) == 0:
        warnings.append("Low-confidence signal: both self and other roles were not represented.")
    low_signal_count = _cue_category_counts(messages).get("low_signal", 0)
    if messages and low_signal_count / len(messages) >= 0.4:
        warnings.append("Low-confidence signal: many messages were too short for stable cue summaries.")
    if audio.get("provided") and audio.get("joined_rows", 0) < 3:
        warnings.append("Low-confidence signal: audio telemetry was sparse after message_id joining.")
    return warnings


def build_report_payload(messages: list[Message], *, audio_matrix: Path | None = None) -> dict[str, Any]:
    message_counts = Counter(message.role for message in messages)
    word_counts: Counter[str] = Counter()
    for message in messages:
        word_counts[message.role] += _word_count(message.text)
    latencies = _latency_events(messages)
    latency_by_role = {
        role: [event["latency_seconds"] for event in latencies if event["responder"] == role] for role in ("self", "other")
    }
    runs = _run_lengths(messages)
    run_lengths_by_role = {
        role: [int(run["length"]) for run in runs if str(run["role"]) == role] for role in ("self", "other")
    }
    cue_counts = _cue_category_counts(messages)
    audio = _audio_summary(audio_matrix, messages)
    ask = _ask_metrics(messages)
    total_messages = len(messages)
    total_words = sum(word_counts.values())
    payload = {
        "report_type": "whatsapp_dynamics_research",
        "privacy": {
            "local_only": True,
            "roles": ["self", "other"],
            "raw_text_emitted": False,
            "participant_names_emitted": False,
            "external_api_calls": False,
        },
        "message_counts_by_role": {role: message_counts.get(role, 0) for role in ("self", "other")},
        "word_counts_by_role": {role: word_counts.get(role, 0) for role in ("self", "other")},
        "average_words_by_role": {role: word_counts.get(role, 0) / max(1, message_counts.get(role, 0)) for role in ("self", "other")},
        "message_count_asymmetry": (message_counts.get("self", 0) - message_counts.get("other", 0)) / max(1, total_messages),
        "word_count_asymmetry": (word_counts.get("self", 0) - word_counts.get("other", 0)) / max(1, total_words),
        "response_latency": {
            "median_seconds_by_role": {
                role: statistics.median(values) if values else None for role, values in latency_by_role.items()
            },
            "distribution_by_role": {role: _summary_distribution(values) for role, values in latency_by_role.items()},
            "same_day_response_rate_by_role": {
                role: sum(1 for value in values if value <= 86400) / max(1, len(values)) for role, values in latency_by_role.items()
            },
            "fast_response_rate_by_role": {
                role: sum(1 for value in values if value <= FAST_RESPONSE_SECONDS) / max(1, len(values))
                for role, values in latency_by_role.items()
            },
        },
        "turn_taking": {
            "turn_starts_by_role": {role: sum(1 for run in runs if str(run["role"]) == role) for role in ("self", "other")},
            "average_consecutive_run_length_by_role": {
                role: statistics.mean(values) if values else 0.0 for role, values in run_lengths_by_role.items()
            },
        },
        "ask_metrics": ask,
        "cue_rates": {cue: count / max(1, total_messages) for cue, count in sorted(cue_counts.items())},
        "top_aggregate_cue_categories": dict(cue_counts.most_common(8)),
        "chronological_cue_shifts": {
            "day": _window_metrics(messages, "day"),
            "week": _window_metrics(messages, "week"),
        },
        "audio": audio,
        "low_signal_warnings": _low_signal_warnings(messages, audio),
        "interpretation_limits": [
            "Aggregate communication patterns require human interpretation.",
            "Cue rates describe observable wording patterns, not inner states.",
            "Audio feature divergence is not an emotion or intent claim.",
        ],
    }
    return payload


def _fmt_seconds(value: float | None) -> str:
    if value is None:
        return "not available"
    if value < 60:
        return f"{value:.0f}s"
    if value < 3600:
        return f"{value / 60:.1f}m"
    if value < 86400:
        return f"{value / 3600:.1f}h"
    return f"{value / 86400:.1f}d"


def _fmt_rate(value: float | None) -> str:
    if value is None:
        return "not available"
    return f"{value * 100:.1f}%"


def _render_report(payload: dict[str, Any]) -> str:
    cues = payload["top_aggregate_cue_categories"]
    cue_lines = [f"- `{cue}`: `{count}` aggregate occurrence(s)" for cue, count in cues.items()] or ["- No aggregate cue categories found."]
    day_shifts = payload["chronological_cue_shifts"]["day"][:6]
    week_shifts = payload["chronological_cue_shifts"]["week"][:6]
    day_lines = [
        f"- `{row['window']}`: messages `{row['message_count_total']}`, cues `{row['cue_counts']}`"
        for row in day_shifts
    ] or ["- No day-level shifts available."]
    week_lines = [
        f"- `{row['window']}`: messages `{row['message_count_total']}`, cues `{row['cue_counts']}`"
        for row in week_shifts
    ] or ["- No week-level shifts available."]
    latency = payload["response_latency"]["median_seconds_by_role"]
    distribution = payload["response_latency"]["distribution_by_role"]
    ask = payload["ask_metrics"]
    audio = payload["audio"]
    warnings = payload["low_signal_warnings"] or ["No low-signal warnings triggered by aggregate checks."]
    report = [
        "# EMOTIONAL TRAJECTORY MAP",
        "",
        "This section describes a possible emotion/cue trajectory using aggregate observable wording patterns and timing clusters. It does not identify inner states.",
        "",
        "Top aggregate cue categories:",
        *cue_lines,
        "",
        "Day-level ordinal cue shifts:",
        *day_lines,
        "",
        "Week-level ordinal cue shifts:",
        *week_lines,
        "",
        "# CONVERSATIONAL ASYMMETRY METRICS",
        "",
        f"- Message counts by role: `self={payload['message_counts_by_role']['self']}`, `other={payload['message_counts_by_role']['other']}`",
        f"- Word counts by role: `self={payload['word_counts_by_role']['self']}`, `other={payload['word_counts_by_role']['other']}`",
        f"- Message count asymmetry: `{payload['message_count_asymmetry']:.3f}`",
        f"- Word count asymmetry: `{payload['word_count_asymmetry']:.3f}`",
        f"- Median response latency by role: `self={_fmt_seconds(latency['self'])}`, `other={_fmt_seconds(latency['other'])}`",
        f"- Response latency p90 by role: `self={_fmt_seconds(distribution['self']['p90_seconds'])}`, `other={_fmt_seconds(distribution['other']['p90_seconds'])}`",
        f"- Direct ask counts by role: `self={ask['direct_ask_count_by_role']['self']}`, `other={ask['direct_ask_count_by_role']['other']}`",
        f"- Unanswered ask candidates by role: `self={ask['unanswered_ask_candidates_by_role']['self']}`, `other={ask['unanswered_ask_candidates_by_role']['other']}`",
        f"- Unclear timing rate: `{_fmt_rate(payload['cue_rates'].get('unclear_timing', 0.0))}`",
        f"- Communication pressure/urgency cue rate: `{_fmt_rate(payload['cue_rates'].get('pressure_urgency', 0.0))}`",
        f"- Repair/reassurance cue rate: `{_fmt_rate(payload['cue_rates'].get('repair_reassurance', 0.0))}`",
        f"- Boundary cue rate: `{_fmt_rate(payload['cue_rates'].get('boundary', 0.0))}`",
        "",
        "# MULTI-MODAL SYNCHRONICITY (TEXT VS. AUDIO)",
        "",
        audio["safe_summary"],
        "",
    ]
    if audio["provided"]:
        report.extend(
            [
                f"- Audio rows joined by message_id: `{audio['joined_rows']}`",
                f"- Feature divergence count: `{audio['feature_divergence']['count']}`",
                f"- Feature divergence rate: `{_fmt_rate(audio['feature_divergence']['rate'])}`",
                f"- Safe interpretation: {audio['feature_divergence']['safe_language']}.",
                "",
            ]
        )
    report.extend(
        [
            "# RELATIONSHIP HEALTH SYNTHESIS",
            "",
            "This is not a relationship health diagnosis.",
            "",
            "Communication pattern summary:",
            "- Reported bottlenecks are aggregate response imbalance, unclear timing, communication pressure, and unanswered ask candidates.",
            "- Repair opportunities are aggregate reassurance, repair wording, boundary-respecting timing, and lower-pressure follow-up.",
            "- Uncertainty limits apply to all outputs; these low-confidence signals require human interpretation.",
            "",
            "Low-signal warnings:",
            *[f"- {warning}" for warning in warnings],
            "",
        ]
    )
    text = "\n".join(report)
    if BLOCKED_REPORT_RE.search(text):
        raise ValueError("Generated report contained blocked claim language.")
    return text


def _write_outputs(payload: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / REPORT_MD
    json_path = output_dir / REPORT_JSON
    md_path.write_text(_render_report(payload), encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return md_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local-only aggregate WhatsApp communication dynamics research report.")
    parser.add_argument("--messages-jsonl", default=str(DEFAULT_MESSAGES))
    parser.add_argument("--audio-matrix")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--allow-synthetic-output", action="store_true")
    args = parser.parse_args(argv)

    messages_path = _resolve(Path(args.messages_jsonl))
    output_dir = _resolve(Path(args.output_dir))
    audio_path = _resolve(Path(args.audio_matrix)) if args.audio_matrix else None

    if not _is_under(messages_path, RESTRICTED_ROOT):
        _safe_error("Refusing input outside data/restricted/private_whatsapp.")
        return 1
    if not messages_path.exists():
        _safe_error("Messages JSONL was not found under the restricted private WhatsApp tree.")
        return 1
    if not _is_under(output_dir, RESTRICTED_ROOT) and not args.allow_synthetic_output:
        _safe_error("Refusing non-restricted output path without --allow-synthetic-output.")
        return 1
    if audio_path and not audio_path.exists():
        _safe_error("Audio matrix path was not found.")
        return 1
    if audio_path and not _is_under(audio_path, RESTRICTED_ROOT):
        _safe_error("Refusing audio matrix outside data/restricted/private_whatsapp.")
        return 1

    try:
        messages = _load_messages(messages_path)
        payload = build_report_payload(messages, audio_matrix=audio_path)
        md_path, json_path = _write_outputs(payload, output_dir)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        _safe_error(f"WhatsApp dynamics analysis failed: {exc}")
        return 1

    print(
        json.dumps(
            {
                "status": "ok",
                "messages_analyzed": len(messages),
                "roles": payload["privacy"]["roles"],
                "report_markdown": str(md_path),
                "report_json": str(json_path),
                "raw_text_emitted": False,
                "participant_names_emitted": False,
                "external_api_calls": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
