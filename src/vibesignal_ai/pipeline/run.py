"""Core pipeline orchestration for VibeSignal AI."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
from typing import Any

from ..contracts.conversation_contract import (
    CONVERSATION_METADATA_SCHEMA_VERSION,
    FEATURE_SET_VERSION,
    SAFETY_POLICY_VERSION,
    SUMMARY_TEMPLATE_VERSION,
    build_conversation_paths,
    normalize_participants,
    validate_conversation_metadata,
)
from ..evidence.export import write_evidence_jsonl
from ..evidence.objects import build_evidence_object
from ..providers.manager import ProviderManager
from ..features.confidence_clarity import analyze_confidence_clarity
from ..features.consistency import analyze_consistency
from ..features.what_changed import analyze_what_changed
from ..features.shift_radar import analyze_shift_radar
from ..ingest.audio_ingest import ingest_audio
from ..ingest.chat_parser import parse_chat_file
from ..ingest.normalization import detect_conversation_language
from ..ingest.segmentation import detect_topical_blocks, group_turns, link_response_pairs
from ..ingest.whatsapp_parser import parse_whatsapp_file
from ..summaries.summary_rewriter import rewrite_summary
from ..ui.payloads import build_payloads
from ..utils.io_utils import ensure_dir, write_csv, write_json
from ..utils.observability import PipelineRecorder, write_observability_artifacts

SOURCE_TYPE_MAP = {
    "whatsapp": "whatsapp_export",
    "pasted_chat": "pasted_chat",
    "audio_note": "audio_note",
    "interview_audio": "interview_audio",
    "generic_audio": "generic_audio",
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return slug or "conversation"


def _copy_input_file(input_path: Path, raw_dir: Path) -> None:
    if input_path.exists() and input_path.is_file():
        raw_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_path, raw_dir / input_path.name)


def _participants_from_messages(messages: list[dict[str, Any]], *, mode: str) -> list[dict[str, str]]:
    seen: list[str] = []
    for message in messages:
        speaker = str(message.get("speaker", "")).strip()
        if not speaker or speaker == "system" or speaker in seen:
            continue
        seen.append(speaker)
    participants = []
    for index, speaker in enumerate(seen, start=1):
        role = "candidate" if mode == "interview" and index == 1 else "unknown"
        participants.append(
            {
                "participant_id": f"participant_{index}",
                "display_name": speaker,
                "role": role,
            }
        )
    return participants


def _required_artifact_paths(
    conversation_root: Path,
    *,
    summary_enabled: bool,
) -> dict[str, Path]:
    return {
        "messages_json": conversation_root / "raw" / "messages.json",
        "segments_json": conversation_root / "processed" / "segments.json",
        "turns_json": conversation_root / "processed" / "turns.json",
        "shift_radar_json": conversation_root / "derived" / "shift_radar.json",
        "consistency_json": conversation_root / "derived" / "consistency.json",
        "confidence_clarity_json": conversation_root / "derived" / "confidence_clarity.json",
        "what_changed_json": conversation_root / "derived" / "what_changed.json",
        "shift_events_csv": conversation_root / "exports" / "shift_events.csv",
        "consistency_events_csv": conversation_root / "exports" / "consistency_events.csv",
        "ui_payloads_json": conversation_root / "exports" / "ui_payloads.json",
        "pattern_summary_json": conversation_root / "exports" / "pattern_summary.json",
        "ui_summary_json": conversation_root / "exports" / "ui_summary.json",
        "evidence_objects_jsonl": conversation_root / "exports" / "evidence_objects.jsonl",
    } | (
        {"optional_summary_json": conversation_root / "exports" / "optional_summary.json"}
        if summary_enabled
        else {}
    )


def _assert_required_artifacts(paths: dict[str, Path]) -> None:
    missing = [name for name, path in paths.items() if not path.exists() or path.stat().st_size <= 0]
    if missing:
        raise RuntimeError(f"required artifacts missing or empty: {', '.join(sorted(missing))}")


def _turn_lookup(turns: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(turn.get("turn_id")): turn for turn in turns}


def _message_id_for_turn(turn: dict[str, Any] | None) -> str:
    if not turn:
        return "unknown"
    message_ids = turn.get("message_ids")
    if isinstance(message_ids, list) and message_ids:
        return str(message_ids[0])
    return str(turn.get("message_id") or "unknown")


def _speaker_role_for_turn(turn: dict[str, Any] | None, *, mode: str) -> str:
    if not turn:
        return "unknown"
    if mode == "interview":
        speaker = str(turn.get("speaker", "")).strip().lower()
        return "interviewer" if speaker in {"interviewer", "recruiter"} else "candidate"
    return "unknown"


def _make_pipeline_evidence(
    *,
    evidence_id: str,
    conversation_id: str,
    source_type: str,
    turn: dict[str, Any] | None,
    mode: str,
    cue_name: str,
    evidence_text: str,
    source_artifact: str,
    source_ref: dict[str, Any],
) -> dict[str, Any] | None:
    text = " ".join(str(evidence_text or "").split())
    if not text:
        return None
    return build_evidence_object(
        evidence_id=evidence_id,
        conversation_id=conversation_id,
        source_type=source_type,
        message_id=_message_id_for_turn(turn),
        turn_id=str((turn or {}).get("turn_id") or "unknown"),
        speaker_role=_speaker_role_for_turn(turn, mode=mode),
        cue_name=cue_name,
        evidence_text=text,
        start_offset=0,
        end_offset=len(text),
        provenance={
            "source_artifact": source_artifact,
            "source_ref": source_ref,
            "offset_note": "Exact character offsets are unavailable from deterministic aggregate outputs; offsets cover the exported evidence text.",
        },
    )


def _build_evidence_objects(
    *,
    conversation_id: str,
    source_type: str,
    mode: str,
    turns: list[dict[str, Any]],
    shift_radar: dict[str, Any],
    consistency: dict[str, Any],
    confidence_clarity: dict[str, Any],
    what_changed: dict[str, Any],
) -> list[dict[str, Any]]:
    lookup = _turn_lookup(turns)
    rows: list[dict[str, Any]] = []

    for index, event in enumerate(shift_radar.get("shift_events", []) or [], start=1):
        turn = lookup.get(str(event.get("change_starts_at_turn_id"))) or lookup.get(str(event.get("start_turn_id")))
        row = _make_pipeline_evidence(
            evidence_id=f"{conversation_id}_shift_{index:04d}",
            conversation_id=conversation_id,
            source_type=source_type,
            turn=turn,
            mode=mode,
            cue_name="conversation_shift",
            evidence_text=str((turn or {}).get("text") or event.get("summary") or ""),
            source_artifact="derived/shift_radar.json",
            source_ref={"event_index": index, "change_starts_at_turn_id": event.get("change_starts_at_turn_id")},
        )
        if row:
            rows.append(row)

    for index, event in enumerate(consistency.get("consistency_events", []) or [], start=1):
        turn = lookup.get(str(event.get("answer_turn_id"))) or lookup.get(str(event.get("question_turn_id")))
        row = _make_pipeline_evidence(
            evidence_id=f"{conversation_id}_consistency_{index:04d}",
            conversation_id=conversation_id,
            source_type=source_type,
            turn=turn,
            mode=mode,
            cue_name=str(event.get("event_type") or "response_consistency"),
            evidence_text=str(event.get("answer_excerpt") or (turn or {}).get("text") or event.get("summary") or ""),
            source_artifact="derived/consistency.json",
            source_ref={"event_index": index, "pair_id": event.get("pair_id")},
        )
        if row:
            rows.append(row)

    for index, segment in enumerate(confidence_clarity.get("strongest_hesitation_segments", []) or [], start=1):
        row = _make_pipeline_evidence(
            evidence_id=f"{conversation_id}_clarity_{index:04d}",
            conversation_id=conversation_id,
            source_type=source_type,
            turn=None,
            mode=mode,
            cue_name="confidence_clarity_marker",
            evidence_text=str(segment.get("excerpt") or segment.get("text") or ""),
            source_artifact="derived/confidence_clarity.json",
            source_ref={"segment_index": index, "segment_id": segment.get("segment_id")},
        )
        if row:
            rows.append(row)

    earliest_turn = lookup.get(str(what_changed.get("earliest_significant_shift_point")))
    if earliest_turn:
        row = _make_pipeline_evidence(
            evidence_id=f"{conversation_id}_what_changed_0001",
            conversation_id=conversation_id,
            source_type=source_type,
            turn=earliest_turn,
            mode=mode,
            cue_name="what_changed_shift_point",
            evidence_text=str(earliest_turn.get("text") or what_changed.get("comparison_summary") or ""),
            source_artifact="derived/what_changed.json",
            source_ref={"earliest_significant_shift_point": what_changed.get("earliest_significant_shift_point")},
        )
        if row:
            rows.append(row)

    if not rows:
        for index, turn in enumerate(turns[:3], start=1):
            row = _make_pipeline_evidence(
                evidence_id=f"{conversation_id}_turn_{index:04d}",
                conversation_id=conversation_id,
                source_type=source_type,
                turn=turn,
                mode=mode,
                cue_name="deterministic_turn_context",
                evidence_text=str(turn.get("text") or ""),
                source_artifact="processed/turns.json",
                source_ref={"turn_id": turn.get("turn_id")},
            )
            if row:
                rows.append(row)
    return rows


def analyze_conversation(
    *,
    input_path: str | Path,
    input_type: str,
    mode: str,
    out_dir: str | Path,
    processing_mode: str = "on_device_only",
    expected_language: str = "en",
    participants: list[Any] | None = None,
    rights_asserted: bool = False,
    provider_mode: str = "local_only",
    provider_name: str | None = None,
    provider_auth_mode: str = "disabled",
    provider_model_name: str | None = None,
    provider_base_url: str | None = None,
    provider_timeout_seconds: int | None = None,
    provider_excerpt_texts: list[str] | None = None,
    provider_api_key: str | None = None,
    provider_secure_storage_available: bool = False,
    provider_credential_present: bool | None = None,
    provider_manager: ProviderManager | None = None,
) -> dict[str, Any]:
    source = Path(input_path).expanduser().resolve()
    conversation_id = _slugify(source.stem)
    output_root = Path(out_dir).expanduser().resolve()
    paths = build_conversation_paths(conversation_id, root=output_root)
    for key in paths:
        ensure_dir(Path(paths[key]))

    conversation_root = Path(paths["conversation_root"])
    raw_dir = Path(paths["raw_dir"])
    processed_dir = Path(paths["processed_dir"])
    derived_dir = Path(paths["derived_dir"])
    exports_dir = Path(paths["exports_dir"])
    logs_dir = Path(paths["logs_dir"])

    recorder = PipelineRecorder(
        route_name="conversation_analysis",
        execution_mode=processing_mode,
    )

    messages: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    segment_metrics: list[dict[str, Any]] = []

    with recorder.stage("ingest"):
        _copy_input_file(source, raw_dir)
        if input_type == "whatsapp":
            messages = parse_whatsapp_file(source)
            segments = [
                {
                    "segment_id": item["message_id"],
                    "speaker": item["speaker"],
                    "start": 0.0,
                    "end": 0.0,
                    "text": item["analysis_text"],
                }
                for item in messages
            ]
        elif input_type == "pasted_chat":
            messages = parse_chat_file(source)
            segments = [
                {
                    "segment_id": item["message_id"],
                    "speaker": item["speaker"],
                    "start": 0.0,
                    "end": 0.0,
                    "text": item["analysis_text"],
                }
                for item in messages
            ]
        else:
            audio_payload = ingest_audio(source, raw_dir=raw_dir, processed_dir=processed_dir)
            messages = audio_payload["messages"]
            segments = audio_payload["segments"]
            segment_metrics = audio_payload["segment_metrics"]

        write_json(raw_dir / "messages.json", messages)
        write_json(processed_dir / "segments.json", segments)

    with recorder.stage("segmentation"):
        turns = group_turns(messages)
        response_pairs = link_response_pairs(turns)
        topical_blocks = detect_topical_blocks(turns)
        write_json(processed_dir / "turns.json", turns)
        write_json(processed_dir / "response_pairs.json", response_pairs)
        write_json(processed_dir / "topical_blocks.json", topical_blocks)

    if not participants:
        participants = _participants_from_messages(messages, mode=mode)
    else:
        participants = normalize_participants(participants)

    with recorder.stage("analysis"):
        shift_radar = analyze_shift_radar(messages, turns=turns, segments=segments)
        consistency = analyze_consistency(messages, turns=turns, response_pairs=response_pairs)
        confidence_clarity = analyze_confidence_clarity(
            segments if segments else messages,
            segment_metrics=segment_metrics or None,
        )
        what_changed = analyze_what_changed(messages, turns=turns)

        write_json(derived_dir / "shift_radar.json", shift_radar)
        write_json(derived_dir / "consistency.json", consistency)
        write_json(derived_dir / "confidence_clarity.json", confidence_clarity)
        write_json(derived_dir / "what_changed.json", what_changed)

    with recorder.stage("exports"):
        payloads = build_payloads(
            shift_radar=shift_radar,
            consistency=consistency,
            confidence_clarity=confidence_clarity,
            what_changed=what_changed,
        )
        write_csv(exports_dir / "shift_events.csv", shift_radar.get("shift_events", []))
        write_csv(exports_dir / "consistency_events.csv", consistency.get("consistency_events", []))
        write_json(exports_dir / "ui_payloads.json", payloads)
        write_json(exports_dir / "pattern_summary.json", payloads["pattern_summary"])
        write_json(exports_dir / "ui_summary.json", payloads["ui_summary"])
        evidence_objects = _build_evidence_objects(
            conversation_id=conversation_id,
            source_type=SOURCE_TYPE_MAP[input_type],
            mode=mode,
            turns=turns,
            shift_radar=shift_radar,
            consistency=consistency,
            confidence_clarity=confidence_clarity,
            what_changed=what_changed,
        )
        write_evidence_jsonl(exports_dir / "evidence_objects.jsonl", evidence_objects)

    summary_payload = None
    if processing_mode == "local_plus_summary":
        with recorder.stage("optional_summary"):
            summary_payload = rewrite_summary(
                {
                    "shift_radar": shift_radar,
                    "consistency": consistency,
                    "confidence_clarity": confidence_clarity,
                    "what_changed": what_changed,
                }
            )
            write_json(exports_dir / "optional_summary.json", summary_payload)

    provider_summary_payload = None
    provider_meta_payload = None
    effective_provider_mode = "local_only"
    with recorder.stage("optional_provider_summary"):
        manager = provider_manager or ProviderManager()
        provider_summary_payload, provider_meta_payload = manager.run_optional_summary(
            provider_mode=provider_mode,
            provider_name=provider_name,
            provider_auth_mode=provider_auth_mode,
            provider_model_name=provider_model_name,
            provider_base_url=provider_base_url,
            provider_timeout_seconds=provider_timeout_seconds,
            provider_api_key=provider_api_key,
            provider_secure_storage_available=provider_secure_storage_available,
            provider_credential_present=provider_credential_present,
            signals={
                "shift_radar": shift_radar,
                "consistency": consistency,
                "confidence_clarity": confidence_clarity,
                "what_changed": what_changed,
            },
            selected_excerpts=provider_excerpt_texts,
        )
        effective_provider_mode = str(
            (provider_meta_payload or {}).get("provider_mode", provider_mode or "local_only")
        ).strip() or "local_only"
        if provider_meta_payload is not None:
            write_json(exports_dir / "provider_response_meta.json", provider_meta_payload)
        if provider_summary_payload is not None:
            write_json(exports_dir / "provider_summary.json", provider_summary_payload)

    detected_language = detect_conversation_language(messages, fallback=expected_language or "unknown")
    metadata = {
        "schema_version": CONVERSATION_METADATA_SCHEMA_VERSION,
        "conversation_id": conversation_id,
        "mode": mode,
        "source_type": SOURCE_TYPE_MAP[input_type],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expected_language": expected_language,
        "detected_language": detected_language,
        "participants": participants,
        "rights_asserted": bool(rights_asserted),
        "processing_mode": processing_mode,
        "provider_mode": effective_provider_mode,
        "provider_name": str((provider_meta_payload or {}).get("provider_name", provider_name or "none") or "none"),
        "provider_auth_mode": str((provider_meta_payload or {}).get("auth_mode", provider_auth_mode or "disabled") or "disabled"),
        "provider_status_at_run": str((provider_meta_payload or {}).get("status", "local_only") or "local_only"),
        "secure_storage_used_for_provider_auth": bool(
            (provider_meta_payload or {}).get("secure_storage_used_for_provider_auth", False)
        ),
        "local_analysis_used": True,
        "external_provider_used": bool((provider_meta_payload or {}).get("external_processing_used", False)),
        "local_result_primary": True,
        "external_summary_secondary": True,
        "feature_set_version": FEATURE_SET_VERSION,
        "safety_policy_version": SAFETY_POLICY_VERSION,
        "summary_template_version": SUMMARY_TEMPLATE_VERSION if processing_mode == "local_plus_summary" else "not_used",
        "ingestion_status": "complete",
        "processing_status": "complete",
        "analysis_status": "complete",
        "notes": [
            "Deterministic-first analysis completed.",
            "Optional summary layer consumes structured signals only.",
            "External provider summaries remain optional and separate from the local artifacts.",
        ],
        "paths": paths,
    }
    write_json(conversation_root / "conversation_metadata.json", metadata)
    errors = validate_conversation_metadata(
        metadata,
        metadata_path=conversation_root / "conversation_metadata.json",
        require_paths_exist=True,
    )
    if errors:
        raise RuntimeError("; ".join(errors))

    with recorder.stage("observability"):
        write_observability_artifacts(logs_dir, recorder)

    required = _required_artifact_paths(
        conversation_root,
        summary_enabled=processing_mode == "local_plus_summary",
    )
    _assert_required_artifacts(required)

    result = {
        "conversation_root": str(conversation_root),
        "metadata_path": str(conversation_root / "conversation_metadata.json"),
        "messages_path": str(raw_dir / "messages.json"),
        "segments_path": str(processed_dir / "segments.json"),
        "turns_path": str(processed_dir / "turns.json"),
        "shift_events_path": str(exports_dir / "shift_events.csv"),
        "consistency_events_path": str(exports_dir / "consistency_events.csv"),
        "ui_payloads_path": str(exports_dir / "ui_payloads.json"),
        "ui_summary_path": str(exports_dir / "ui_summary.json"),
        "evidence_objects_path": str(exports_dir / "evidence_objects.jsonl"),
        "local_analysis_used": True,
        "external_provider_used": bool((provider_meta_payload or {}).get("external_processing_used", False)),
        "provider_mode": effective_provider_mode,
        "provider_status_at_run": str((provider_meta_payload or {}).get("status", "local_only") or "local_only"),
        "secure_storage_used_for_provider_auth": bool(
            (provider_meta_payload or {}).get("secure_storage_used_for_provider_auth", False)
        ),
        "local_result_primary": True,
        "external_summary_secondary": True,
        "provider_output_path": str(exports_dir / "provider_summary.json") if provider_summary_payload is not None else None,
        "provider_response_meta_path": str(exports_dir / "provider_response_meta.json") if provider_meta_payload is not None else None,
    }
    if summary_payload is not None:
        result["summary_path"] = str(exports_dir / "optional_summary.json")
    return result
