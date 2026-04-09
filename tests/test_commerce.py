from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from vibesignal_ai.commerce.analysis_runner import run_metered_analysis
from vibesignal_ai.commerce.api import handle_commerce_request
from vibesignal_ai.commerce.service import CommerceService
from vibesignal_ai.commerce.verification import build_verification_result
from vibesignal_ai.commerce.models import PurchaseVerificationRequest
import vibesignal_ai.commerce.analysis_runner as analysis_runner_module


def _service(tmp_path):
    return CommerceService(db_path=tmp_path / "commerce.sqlite3")


def _user(service: CommerceService, *, device_installation_id: str = "device-ios-1", platform: str = "ios") -> str:
    return service.get_or_create_user(
        device_installation_id=device_installation_id,
        platform=platform,
    ).app_user_id


def test_free_limit_counts_completed_analyses_only(tmp_path, monkeypatch) -> None:
    service = _service(tmp_path)
    app_user_id = _user(service)

    for index in range(9):
        assert service.record_completed_analysis(
            app_user_id=app_user_id,
            analysis_id=f"analysis_{index}",
            conversation_id=f"conversation_{index}",
        )

    entitlement = service.get_entitlement(app_user_id)
    assert entitlement.usage_count == 9
    assert entitlement.free_remaining == 1
    assert service.check_analysis_access(app_user_id=app_user_id).allowed is True

    def _boom(**kwargs):
        raise RuntimeError("analysis failed before completion")

    monkeypatch.setattr(analysis_runner_module, "analyze_conversation", _boom)
    with pytest.raises(RuntimeError):
        run_metered_analysis(
            commerce_service=service,
            app_user_id=app_user_id,
            input_path="unused",
            input_type="whatsapp",
            mode="relationship_chat",
            out_dir=tmp_path / "outputs",
            rights_asserted=True,
        )

    entitlement_after_failure = service.get_entitlement(app_user_id)
    assert entitlement_after_failure.usage_count == 9
    assert entitlement_after_failure.free_remaining == 1

    assert service.record_completed_analysis(
        app_user_id=app_user_id,
        analysis_id="analysis_10",
        conversation_id="conversation_10",
    )
    blocked = service.get_entitlement(app_user_id)
    assert blocked.usage_count == 10
    assert blocked.free_remaining == 0
    assert blocked.blocked_reason == "free_limit_reached"
    assert service.check_analysis_access(app_user_id=app_user_id).allowed is False


def test_subscription_active_unlocks_after_free_limit(tmp_path) -> None:
    service = _service(tmp_path)
    app_user_id = _user(service)
    for index in range(10):
        service.record_completed_analysis(
            app_user_id=app_user_id,
            analysis_id=f"analysis_{index}",
            conversation_id=f"conversation_{index}",
        )

    request = PurchaseVerificationRequest(
        app_user_id=app_user_id,
        platform="ios",
        product_id="vibesignal_pro_monthly_ios",
        receipt_or_token="ios-token-active",
        transaction_id="tx-active",
        purchase_id="purchase-active",
    )
    result = build_verification_result(
        request=request,
        verification_state="verified_active",
        purchase_id="purchase-active",
        transaction_id="tx-active",
        expires_at=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        started_at=datetime.now(timezone.utc).isoformat(),
    )
    purchase = service.ingest_purchase_verification(request=request, result=result)
    entitlement = service.get_entitlement(app_user_id)

    assert purchase.purchase_token_hash
    assert entitlement.subscription_status == "active"
    assert entitlement.entitlement_state == "subscription_active"
    assert entitlement.blocked_reason == ""
    assert service.check_analysis_access(app_user_id=app_user_id).allowed is True


def test_expired_subscription_blocks_after_limit(tmp_path) -> None:
    service = _service(tmp_path)
    app_user_id = _user(service)
    for index in range(10):
        service.record_completed_analysis(
            app_user_id=app_user_id,
            analysis_id=f"analysis_{index}",
            conversation_id=f"conversation_{index}",
        )

    request = PurchaseVerificationRequest(
        app_user_id=app_user_id,
        platform="android",
        product_id="vibesignal_pro_monthly_android",
        receipt_or_token="android-token-expired",
        transaction_id="tx-expired",
        purchase_id="purchase-expired",
    )
    result = build_verification_result(
        request=request,
        verification_state="verified_expired",
        purchase_id="purchase-expired",
        transaction_id="tx-expired",
        expires_at=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        started_at=(datetime.now(timezone.utc) - timedelta(days=31)).isoformat(),
    )
    service.ingest_purchase_verification(request=request, result=result)

    entitlement = service.get_entitlement(app_user_id)
    access = service.check_analysis_access(app_user_id=app_user_id)
    assert entitlement.subscription_status == "expired"
    assert entitlement.blocked_reason == "subscription_expired"
    assert access.allowed is False
    assert access.blocked_reason == "subscription_expired"


def test_restore_recomputes_entitlement(tmp_path) -> None:
    service = _service(tmp_path)
    app_user_id = _user(service)
    for index in range(10):
        service.record_completed_analysis(
            app_user_id=app_user_id,
            analysis_id=f"analysis_{index}",
            conversation_id=f"conversation_{index}",
        )

    restore = service.restore_purchases(
        app_user_id=app_user_id,
        verification_results=[
            build_verification_result(
                request=PurchaseVerificationRequest(
                    app_user_id=app_user_id,
                    platform="ios",
                    product_id="vibesignal_pro_monthly_ios",
                    receipt_or_token="restore-token",
                    purchase_id="purchase-restore",
                    transaction_id="tx-restore",
                ),
                verification_state="verified_grace_period",
                purchase_id="purchase-restore",
                transaction_id="tx-restore",
                expires_at=(datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
                started_at=datetime.now(timezone.utc).isoformat(),
            )
        ],
    )

    assert restore.restored_count == 1
    assert restore.entitlement.subscription_status == "grace_period"
    assert restore.entitlement.entitlement_state == "subscription_active"


def test_verification_unavailable_maps_to_purchase_unverified_after_limit(tmp_path) -> None:
    service = _service(tmp_path)
    app_user_id = _user(service)
    for index in range(10):
        service.record_completed_analysis(
            app_user_id=app_user_id,
            analysis_id=f"analysis_{index}",
            conversation_id=f"conversation_{index}",
        )

    request = PurchaseVerificationRequest(
        app_user_id=app_user_id,
        platform="ios",
        product_id="vibesignal_pro_monthly_ios",
        receipt_or_token="receipt-verification-unavailable",
        purchase_id="purchase-unavailable",
    )
    result = build_verification_result(
        request=request,
        verification_state="verification_unavailable",
        purchase_id="purchase-unavailable",
    )
    service.ingest_purchase_verification(request=request, result=result)
    entitlement = service.get_entitlement(app_user_id)

    assert entitlement.purchase_verification_state == "verification_unavailable"
    assert entitlement.blocked_reason == "purchase_unverified"


def test_metered_analysis_blocks_for_provider_and_records_success(tmp_path, monkeypatch) -> None:
    service = _service(tmp_path)
    app_user_id = _user(service)

    blocked = run_metered_analysis(
        commerce_service=service,
        app_user_id=app_user_id,
        requires_provider=True,
        provider_consent_confirmed=False,
        input_path="unused",
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path / "blocked",
        rights_asserted=True,
    )
    assert blocked["allowed"] is False
    assert blocked["blocked_reason"] == "missing_consent"
    assert service.get_entitlement(app_user_id).usage_count == 0

    blocked_storage = run_metered_analysis(
        commerce_service=service,
        app_user_id=app_user_id,
        requires_provider=True,
        provider_consent_confirmed=True,
        provider_secure_storage_available=False,
        input_path="unused",
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path / "blocked_storage",
        rights_asserted=True,
    )
    assert blocked_storage["blocked_reason"] == "secure_storage_unavailable"

    blocked_provider = run_metered_analysis(
        commerce_service=service,
        app_user_id=app_user_id,
        requires_provider=True,
        provider_consent_confirmed=True,
        provider_secure_storage_available=True,
        provider_validation_status="invalid_credentials",
        input_path="unused",
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path / "blocked_provider",
        rights_asserted=True,
    )
    assert blocked_provider["blocked_reason"] == "provider_not_ready"

    monkeypatch.setattr(
        analysis_runner_module,
        "analyze_conversation",
        lambda **kwargs: {"conversation_id": "conversation-pass", "conversation_root": str(tmp_path / "conversation-pass")},
    )

    allowed = run_metered_analysis(
        commerce_service=service,
        app_user_id=app_user_id,
        input_path="unused",
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path / "allowed",
        rights_asserted=True,
    )
    assert allowed["allowed"] is True
    assert allowed["usage_recorded"] is True
    assert allowed["entitlement"]["usage_count"] == 1
    assert allowed["entitlement"]["free_remaining"] == 9


def test_commerce_api_fetches_entitlement_and_accepts_purchase_submission(tmp_path) -> None:
    service = _service(tmp_path)
    registered = handle_commerce_request(
        service,
        action="register_anonymous_user",
        payload={
            "device_installation_id": "device-api-1",
            "platform": "ios",
        },
    )
    app_user_id = registered["app_user"]["app_user_id"]

    entitlement_response = handle_commerce_request(
        service,
        action="fetch_entitlement",
        payload={"app_user_id": app_user_id},
    )
    assert entitlement_response["status"] == "entitlement_loaded"
    assert entitlement_response["entitlement"]["free_remaining"] == 10

    verification_response = handle_commerce_request(
        service,
        action="submit_purchase_verification",
        payload={
            "app_user_id": app_user_id,
            "platform": "ios",
            "product_id": "vibesignal_pro_monthly_ios",
            "purchase_id": "purchase-api-1",
            "purchase_artifact": {
                "artifact_type": "apple_app_store_receipt",
                "receipt_data_b64": "receipt-test",
                "transaction_id": "tx-api-1",
                "environment": "Sandbox",
            },
        },
    )
    assert verification_response["ok"] is True
    assert verification_response["status"] == "verification_unavailable"
    assert verification_response["purchase"]["purchase_token_hash"]


def test_commerce_api_rejects_malformed_purchase_artifact(tmp_path) -> None:
    service = _service(tmp_path)
    app_user_id = _user(service)

    response = handle_commerce_request(
        service,
        action="submit_purchase_verification",
        payload={
            "app_user_id": app_user_id,
            "platform": "android",
            "product_id": "vibesignal_pro_monthly_android",
            "purchase_artifact": {
                "artifact_type": "google_play_purchase_token",
                "purchase_token": "",
                "package_name": "",
            },
        },
    )

    assert response["ok"] is False
    assert response["status"] == "invalid_purchase_artifact"


def test_commerce_api_requires_device_identity_for_anonymous_entitlement_bootstrap(tmp_path) -> None:
    service = _service(tmp_path)

    response = handle_commerce_request(
        service,
        action="fetch_entitlement",
        payload={
            "platform": "ios",
        },
    )

    assert response["ok"] is False
    assert response["status"] == "invalid_identity"
