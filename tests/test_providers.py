from __future__ import annotations

import json
from pathlib import Path

from vibesignal_ai.config import provider_flags
from vibesignal_ai.providers.base import BaseProvider
from vibesignal_ai.providers.manager import ProviderManager
from vibesignal_ai.providers.models import ProviderExecutionResult
from vibesignal_ai.providers.validation import VALIDATION_MESSAGES
from vibesignal_ai.pipeline.run import analyze_conversation
from vibesignal_ai.safety.validator import validate_payload
from vibesignal_ai.ui.provider_consent import build_provider_consent_payload
from vibesignal_ai.ui.provider_status import build_provider_status_payload


class _SafeFakeProvider(BaseProvider):
    name = "openai"
    sdk_name = "fake"

    def is_available(self) -> bool:
        return True

    def summarize(self, *, config, prompt_payload):  # type: ignore[override]
        return ProviderExecutionResult(
            provider_name=self.name,
            model_name=config.model_name,
            output_text="Later replies look shorter and less detailed than earlier ones.",
            raw_response_meta={"fake": True},
        )


class _UnsafeFakeProvider(BaseProvider):
    name = "openai"
    sdk_name = "fake"

    def is_available(self) -> bool:
        return True

    def summarize(self, *, config, prompt_payload):  # type: ignore[override]
        return ProviderExecutionResult(
            provider_name=self.name,
            model_name=config.model_name,
            output_text="This clearly means they are lying.",
            raw_response_meta={"fake": True},
        )


class _ValidatingFakeProvider(BaseProvider):
    name = "openai"
    sdk_name = "fake"

    def __init__(self, validation_status: str = "ready") -> None:
        self.validation_status = validation_status

    def is_available(self) -> bool:
        return True

    def summarize(self, *, config, prompt_payload):  # type: ignore[override]
        return ProviderExecutionResult(
            provider_name=self.name,
            model_name=config.model_name,
            output_text="Later replies look shorter and less detailed than earlier ones.",
            raw_response_meta={"fake": True},
        )

    def validate_credentials(self, *, config, consent_confirmed=False):  # type: ignore[override]
        from vibesignal_ai.providers.validation import build_validation_result

        return build_validation_result(
            config=config,
            status=self.validation_status,
            consent_confirmed=consent_confirmed,
        )


def test_provider_flags_default_off() -> None:
    snapshot = provider_flags.provider_flags_snapshot()
    assert snapshot["enable_external_providers"] is False
    assert snapshot["enable_openai_provider"] is False
    assert snapshot["enable_anthropic_provider"] is False
    assert snapshot["enable_groq_provider"] is False


def test_provider_manager_fails_closed_when_not_configured() -> None:
    manager = ProviderManager()
    summary, meta = manager.run_optional_summary(
        provider_mode="external_summary_optional",
        provider_name="openai",
        provider_auth_mode="backend_proxy",
        signals={},
    )
    assert summary is None
    assert meta["provider_mode"] == "provider_disabled"
    assert meta["external_processing_used"] is False


def test_provider_manager_requires_secure_storage_for_byok(monkeypatch) -> None:
    monkeypatch.setattr(provider_flags, "ENABLE_EXTERNAL_PROVIDERS", True)
    monkeypatch.setattr(provider_flags, "ENABLE_OPENAI_PROVIDER", True)
    manager = ProviderManager()
    summary, meta = manager.run_optional_summary(
        provider_mode="external_summary_optional",
        provider_name="openai",
        provider_auth_mode="byok",
        provider_secure_storage_available=False,
        signals={},
    )
    assert summary is None
    assert meta["status"] == "secure_storage_unavailable"
    assert meta["provider_status"]["secure_storage_available"] is False


def test_provider_manager_requires_stored_credential_for_byok(monkeypatch) -> None:
    monkeypatch.setattr(provider_flags, "ENABLE_EXTERNAL_PROVIDERS", True)
    monkeypatch.setattr(provider_flags, "ENABLE_OPENAI_PROVIDER", True)
    manager = ProviderManager()
    summary, meta = manager.run_optional_summary(
        provider_mode="external_summary_optional",
        provider_name="openai",
        provider_auth_mode="byok",
        provider_secure_storage_available=True,
        provider_credential_present=False,
        signals={},
    )
    assert summary is None
    assert meta["status"] == "provider_enabled_no_credential"
    assert meta["provider_status"]["credential_present"] is False


def test_provider_manager_safety_rejects_unsafe_output(monkeypatch) -> None:
    monkeypatch.setattr(provider_flags, "ENABLE_EXTERNAL_PROVIDERS", True)
    monkeypatch.setattr(provider_flags, "ENABLE_OPENAI_PROVIDER", True)
    manager = ProviderManager(registry={"openai": _UnsafeFakeProvider()})
    summary, meta = manager.run_optional_summary(
        provider_mode="external_summary_optional",
        provider_name="openai",
        provider_auth_mode="backend_proxy",
        signals={},
    )
    assert summary is not None
    assert summary["safety_validated"] is False
    assert summary["output_text"] == ""
    assert meta["status"] == "safety_rejected"


def test_provider_validation_surface_requires_consent(monkeypatch) -> None:
    monkeypatch.setattr(provider_flags, "ENABLE_EXTERNAL_PROVIDERS", True)
    monkeypatch.setattr(provider_flags, "ENABLE_OPENAI_PROVIDER", True)
    manager = ProviderManager(registry={"openai": _ValidatingFakeProvider()})
    result = manager.validate_provider_connection(
        provider_name="openai",
        provider_auth_mode="byok",
        provider_api_key="sk-test",
        provider_secure_storage_available=True,
        provider_credential_present=True,
        consent_confirmed=False,
    )
    assert result.status == "consent_required"
    assert result.user_message == VALIDATION_MESSAGES["consent_required"]


def test_provider_validation_surface_returns_ready_when_live_path_is_ready(monkeypatch) -> None:
    monkeypatch.setattr(provider_flags, "ENABLE_EXTERNAL_PROVIDERS", True)
    monkeypatch.setattr(provider_flags, "ENABLE_OPENAI_PROVIDER", True)
    manager = ProviderManager(registry={"openai": _ValidatingFakeProvider("ready")})
    result = manager.validate_provider_connection(
        provider_name="openai",
        provider_auth_mode="byok",
        provider_api_key="sk-test",
        provider_secure_storage_available=True,
        provider_credential_present=True,
        consent_confirmed=True,
    )
    assert result.status == "ready"
    assert result.ready is True


def test_provider_validation_surface_fails_closed_without_key(monkeypatch) -> None:
    monkeypatch.setattr(provider_flags, "ENABLE_EXTERNAL_PROVIDERS", True)
    monkeypatch.setattr(provider_flags, "ENABLE_OPENAI_PROVIDER", True)
    manager = ProviderManager(registry={"openai": _ValidatingFakeProvider()})
    result = manager.validate_provider_connection(
        provider_name="openai",
        provider_auth_mode="byok",
        provider_secure_storage_available=True,
        provider_credential_present=False,
        consent_confirmed=True,
    )
    assert result.status == "missing_credentials"
    assert result.ready is False


def test_provider_run_gate_blocks_when_validation_failed() -> None:
    gate = ProviderManager().gate_external_summary_request(
        provider_name="openai",
        consent_confirmed=True,
        secure_storage_available=True,
        credential_present=True,
        validation_status="invalid_credentials",
    )
    assert gate.allowed is False
    assert gate.status == "invalid_credentials"


def test_provider_run_gate_blocks_when_provider_missing() -> None:
    gate = ProviderManager().gate_external_summary_request(
        provider_name="",
        consent_confirmed=True,
        secure_storage_available=True,
        credential_present=False,
        validation_status="missing_credentials",
    )
    assert gate.allowed is False
    assert gate.status == "provider_not_configured"


def test_pipeline_default_mode_stays_local_only(tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "relationship_chat_hardened.txt"
    result = analyze_conversation(
        input_path=fixture,
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path,
        rights_asserted=True,
    )
    assert result["provider_mode"] == "local_only"
    assert result["local_analysis_used"] is True
    assert result["external_provider_used"] is False
    assert result["provider_status_at_run"] == "local_only"
    meta = json.loads(Path(result["provider_response_meta_path"]).read_text(encoding="utf-8"))
    assert meta["status"] == "local_only"
    assert meta["provider_status"]["status"] == "local_only"


def test_pipeline_provider_disabled_fallback_keeps_local_outputs(tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "relationship_chat_hardened.txt"
    result = analyze_conversation(
        input_path=fixture,
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path,
        rights_asserted=True,
        provider_mode="external_summary_optional",
        provider_name="openai",
        provider_auth_mode="backend_proxy",
    )
    assert result["external_provider_used"] is False
    assert Path(result["ui_summary_path"]).exists()
    meta = json.loads(Path(result["provider_response_meta_path"]).read_text(encoding="utf-8"))
    assert meta["provider_mode"] == "provider_disabled"
    assert result["local_result_primary"] is True
    assert result["external_summary_secondary"] is True


def test_pipeline_external_outputs_stay_separate(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(provider_flags, "ENABLE_EXTERNAL_PROVIDERS", True)
    monkeypatch.setattr(provider_flags, "ENABLE_OPENAI_PROVIDER", True)
    fixture = Path(__file__).parent / "fixtures" / "relationship_chat_hardened.txt"
    manager = ProviderManager(registry={"openai": _SafeFakeProvider()})

    result = analyze_conversation(
        input_path=fixture,
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path,
        rights_asserted=True,
        provider_mode="external_summary_optional",
        provider_name="openai",
        provider_auth_mode="backend_proxy",
        provider_manager=manager,
    )

    assert result["external_provider_used"] is True
    assert result["provider_output_path"] is not None
    assert result["provider_output_path"] != result["ui_summary_path"]
    provider_summary = json.loads(Path(result["provider_output_path"]).read_text(encoding="utf-8"))
    assert provider_summary["output_label"] == "external_ai_summary"
    assert provider_summary["safety_validated"] is True
    assert validate_payload(provider_summary) == []


def test_provider_consent_payload_generation() -> None:
    payload = build_provider_consent_payload("openai", auth_mode="byok")
    assert payload["provider_name"] == "openai"
    assert payload["auth_mode"] == "byok"
    assert validate_payload(payload) == []


def test_provider_status_payload_truthfully_reflects_secure_storage() -> None:
    payload = build_provider_status_payload(
        provider_name="openai",
        display_name="OpenAI",
        enabled=True,
        auth_mode="byok",
        provider_mode="external_summary_optional",
        secure_storage_available=False,
        credential_present=False,
    )
    assert payload["status"] == "secure_storage_unavailable"
    assert payload["can_request_summary"] is False
    assert validate_payload(payload) == []


def test_provider_status_payload_marks_ready_when_secure_credential_exists() -> None:
    payload = build_provider_status_payload(
        provider_name="openai",
        display_name="OpenAI",
        enabled=True,
        auth_mode="byok",
        provider_mode="external_summary_optional",
        secure_storage_available=True,
        credential_present=True,
    )
    assert payload["status"] == "provider_ready"
    assert payload["can_request_summary"] is True
