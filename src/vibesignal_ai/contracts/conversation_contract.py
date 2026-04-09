"""Canonical conversation metadata contract for VibeSignal AI."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

CONVERSATION_METADATA_SCHEMA_VERSION = "1.3.0"
FEATURE_SET_VERSION = "0.2.0"
SAFETY_POLICY_VERSION = "0.2.0"
SUMMARY_TEMPLATE_VERSION = "0.2.0"

REQUIRED_FIELDS = (
    "conversation_id",
    "mode",
    "source_type",
    "created_at",
    "expected_language",
    "participants",
    "rights_asserted",
    "processing_mode",
    "provider_mode",
    "provider_name",
    "provider_auth_mode",
    "provider_status_at_run",
    "secure_storage_used_for_provider_auth",
    "local_analysis_used",
    "external_provider_used",
    "local_result_primary",
    "external_summary_secondary",
    "feature_set_version",
    "safety_policy_version",
    "summary_template_version",
    "ingestion_status",
    "processing_status",
    "analysis_status",
    "notes",
    "paths",
)

BOOLEAN_FIELDS = {
    "rights_asserted",
    "secure_storage_used_for_provider_auth",
    "local_analysis_used",
    "external_provider_used",
    "local_result_primary",
    "external_summary_secondary",
}
STATUS_FIELDS = {"ingestion_status", "processing_status", "analysis_status"}

ALLOWED_STATUS_VALUES = {
    "not_started",
    "queued",
    "in_progress",
    "complete",
    "blocked",
    "needs_review",
    "not_applicable",
}
ALLOWED_MODES = {"relationship_chat", "interview", "generic", "mixed_session"}
ALLOWED_SOURCE_TYPES = {
    "whatsapp_export",
    "pasted_chat",
    "audio_note",
    "interview_audio",
    "generic_audio",
    "mixed_text_audio",
}
ALLOWED_PROCESSING_MODES = {"on_device_only", "local_plus_summary"}
ALLOWED_PROVIDER_MODES = {"local_only", "external_summary_optional", "provider_disabled"}
ALLOWED_PROVIDER_AUTH_MODES = {"byok", "backend_proxy", "disabled"}
ALLOWED_PROVIDER_STATUSES = {
    "local_only",
    "provider_disabled",
    "provider_not_configured",
    "secure_storage_unavailable",
    "provider_enabled_no_credential",
    "provider_ready",
    "provider_error",
    "success",
    "safety_rejected",
}
ALLOWED_PARTICIPANT_ROLES = {"self", "other", "interviewer", "candidate", "unknown"}
REQUIRED_PATH_KEYS = (
    "conversation_root",
    "raw_dir",
    "processed_dir",
    "derived_dir",
    "logs_dir",
    "exports_dir",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_conversation_paths(
    conversation_id: str,
    *,
    root: str | Path = "outputs",
) -> dict[str, str]:
    normalized = str(conversation_id).strip()
    conversation_root = Path(root) / normalized
    return {
        "conversation_root": str(conversation_root),
        "raw_dir": str(conversation_root / "raw"),
        "processed_dir": str(conversation_root / "processed"),
        "derived_dir": str(conversation_root / "derived"),
        "logs_dir": str(conversation_root / "logs"),
        "exports_dir": str(conversation_root / "exports"),
    }


def load_conversation_metadata(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Conversation metadata must be a JSON object: {path}")
    return payload


def _is_non_empty(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if value is None:
        return False
    if isinstance(value, list):
        return True
    return str(value).strip() != ""


def _is_iso_datetime(text: Any) -> bool:
    candidate = str(text or "").strip()
    if not candidate:
        return False
    try:
        datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _resolve_relative_path(value: Any, *, base_dir: Path | None = None) -> Path | None:
    text = str(value or "").strip()
    if not text:
        return None
    path = Path(text)
    if path.is_absolute():
        return path
    root = base_dir or repo_root()
    return (root / path).resolve()


def normalize_participants(participants: list[Any]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(participants, start=1):
        if isinstance(item, str):
            display_name = item.strip()
            if not display_name:
                continue
            normalized.append(
                {
                    "participant_id": f"participant_{index}",
                    "display_name": display_name,
                    "role": "unknown",
                }
            )
            continue
        if isinstance(item, dict):
            display_name = str(item.get("display_name", "")).strip()
            participant_id = str(item.get("participant_id", f"participant_{index}")).strip()
            role = str(item.get("role", "unknown")).strip() or "unknown"
            if not display_name or not participant_id:
                continue
            normalized.append(
                {
                    "participant_id": participant_id,
                    "display_name": display_name,
                    "role": role,
                }
            )
    return normalized


def validate_conversation_metadata(
    payload: dict[str, Any],
    *,
    metadata_path: str | Path | None = None,
    require_paths_exist: bool = False,
) -> list[str]:
    if not isinstance(payload, dict):
        return ["conversation metadata payload must be a JSON object"]

    errors: list[str] = []
    base_dir = Path(metadata_path).resolve().parent if metadata_path else repo_root()

    schema_version = str(
        payload.get("schema_version", CONVERSATION_METADATA_SCHEMA_VERSION)
    )
    if schema_version != CONVERSATION_METADATA_SCHEMA_VERSION:
        errors.append(
            "schema_version must be "
            f"{CONVERSATION_METADATA_SCHEMA_VERSION}, got {schema_version}"
        )

    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing required field: {field}")
            continue
        if field == "notes":
            continue
        if not _is_non_empty(payload.get(field)):
            errors.append(f"required field is empty: {field}")

    if payload.get("mode") not in ALLOWED_MODES:
        errors.append(f"mode must be one of {sorted(ALLOWED_MODES)}")

    source_type = str(payload.get("source_type", "")).strip()
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(
            f"source_type must be one of {sorted(ALLOWED_SOURCE_TYPES)}, got {source_type!r}"
        )

    processing_mode = str(payload.get("processing_mode", "")).strip()
    if processing_mode not in ALLOWED_PROCESSING_MODES:
        errors.append(
            "processing_mode must be one of "
            f"{sorted(ALLOWED_PROCESSING_MODES)}, got {processing_mode!r}"
        )

    provider_mode = str(payload.get("provider_mode", "")).strip()
    if provider_mode not in ALLOWED_PROVIDER_MODES:
        errors.append(
            "provider_mode must be one of "
            f"{sorted(ALLOWED_PROVIDER_MODES)}, got {provider_mode!r}"
        )

    provider_auth_mode = str(payload.get("provider_auth_mode", "")).strip()
    if provider_auth_mode not in ALLOWED_PROVIDER_AUTH_MODES:
        errors.append(
            "provider_auth_mode must be one of "
            f"{sorted(ALLOWED_PROVIDER_AUTH_MODES)}, got {provider_auth_mode!r}"
        )

    provider_status_at_run = str(payload.get("provider_status_at_run", "")).strip()
    if provider_status_at_run not in ALLOWED_PROVIDER_STATUSES:
        errors.append(
            "provider_status_at_run must be one of "
            f"{sorted(ALLOWED_PROVIDER_STATUSES)}, got {provider_status_at_run!r}"
        )

    if not _is_iso_datetime(payload.get("created_at")):
        errors.append("created_at must be an ISO-8601 datetime string")

    participants = payload.get("participants")
    if not isinstance(participants, list):
        errors.append("participants must be a JSON array")
    else:
        normalized = normalize_participants(participants)
        if not normalized:
            errors.append("participants must include at least one non-empty participant")
        for item in normalized:
            role = str(item.get("role", "")).strip()
            if role not in ALLOWED_PARTICIPANT_ROLES:
                errors.append(
                    f"participant role must be one of {sorted(ALLOWED_PARTICIPANT_ROLES)}, got {role!r}"
                )

    for field in BOOLEAN_FIELDS:
        if field in payload and not isinstance(payload.get(field), bool):
            errors.append(f"{field} must be a JSON boolean")

    for field in STATUS_FIELDS:
        value = str(payload.get(field, "")).strip()
        if value not in ALLOWED_STATUS_VALUES:
            errors.append(
                f"{field} must be one of {sorted(ALLOWED_STATUS_VALUES)}, got {value!r}"
            )

    for field in ("feature_set_version", "safety_policy_version", "summary_template_version"):
        if not str(payload.get(field, "")).strip():
            errors.append(f"{field} must be populated")

    language = str(payload.get("expected_language", "")).strip().lower()
    if not language:
        errors.append("expected_language must be populated")

    paths = payload.get("paths")
    if not isinstance(paths, dict):
        errors.append("paths must be a JSON object")
    else:
        for key in REQUIRED_PATH_KEYS:
            if key not in paths or not str(paths.get(key, "")).strip():
                errors.append(f"paths missing required key: {key}")
        if require_paths_exist:
            for key in REQUIRED_PATH_KEYS:
                candidate = _resolve_relative_path(paths.get(key), base_dir=base_dir)
                if candidate is None or not candidate.exists():
                    errors.append(f"path does not exist for {key}: {paths.get(key)}")

    return errors


def path_existence_errors(payload: dict[str, Any]) -> list[str]:
    return validate_conversation_metadata(payload, require_paths_exist=True)
