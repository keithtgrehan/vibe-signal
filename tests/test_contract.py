from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from vibesignal_ai.contracts.conversation_contract import (
    CONVERSATION_METADATA_SCHEMA_VERSION,
    FEATURE_SET_VERSION,
    SAFETY_POLICY_VERSION,
    SUMMARY_TEMPLATE_VERSION,
    build_conversation_paths,
    validate_conversation_metadata,
)


def test_conversation_contract_validation_with_enriched_participants(tmp_path: Path) -> None:
    paths = build_conversation_paths("demo-chat", root=tmp_path)
    for value in paths.values():
        Path(value).mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": CONVERSATION_METADATA_SCHEMA_VERSION,
        "conversation_id": "demo-chat",
        "mode": "mixed_session",
        "source_type": "mixed_text_audio",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expected_language": "en",
        "participants": [
            {"participant_id": "self_1", "display_name": "Alex", "role": "self"},
            {"participant_id": "other_1", "display_name": "Sam", "role": "other"},
        ],
        "rights_asserted": True,
        "processing_mode": "local_plus_summary",
        "provider_mode": "local_only",
        "provider_name": "none",
        "provider_auth_mode": "disabled",
        "provider_status_at_run": "local_only",
        "secure_storage_used_for_provider_auth": False,
        "local_analysis_used": True,
        "external_provider_used": False,
        "local_result_primary": True,
        "external_summary_secondary": True,
        "feature_set_version": FEATURE_SET_VERSION,
        "safety_policy_version": SAFETY_POLICY_VERSION,
        "summary_template_version": SUMMARY_TEMPLATE_VERSION,
        "ingestion_status": "complete",
        "processing_status": "complete",
        "analysis_status": "complete",
        "notes": [],
        "paths": paths,
    }

    assert validate_conversation_metadata(payload, require_paths_exist=True) == []
