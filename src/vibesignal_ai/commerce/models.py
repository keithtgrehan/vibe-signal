"""Domain models for usage metering, purchases, and entitlements."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PURCHASE_ARTIFACT_TYPES = (
    "apple_app_store_receipt",
    "google_play_purchase_token",
)

PURCHASE_VERIFICATION_STATES = (
    "verified_active",
    "verified_grace_period",
    "verified_expired",
    "revoked",
    "refunded",
    "unverified",
    "invalid_receipt_or_token",
    "verification_unavailable",
)

SUBSCRIPTION_STATUSES = (
    "inactive",
    "active",
    "grace_period",
    "expired",
    "revoked",
    "refunded",
    "unverified",
    "invalid_receipt_or_token",
    "verification_unavailable",
)

ENTITLEMENT_STATES = (
    "free_available",
    "subscription_active",
    "blocked",
)

BLOCKED_REASONS = (
    "free_limit_reached",
    "subscription_inactive",
    "subscription_expired",
    "purchase_unverified",
    "provider_not_ready",
    "missing_consent",
    "secure_storage_unavailable",
)


@dataclass(frozen=True)
class BillingProduct:
    product_id: str
    platform: str
    display_name: str
    price_display: str
    subscription_period: str = "P1M"
    product_type: str = "auto_renewing_subscription"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AppUserRecord:
    app_user_id: str
    device_installation_id: str
    platform: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PurchaseVerificationRequest:
    app_user_id: str
    platform: str
    product_id: str
    receipt_or_token: str
    artifact_type: str = ""
    transaction_id: str = ""
    original_transaction_id: str = ""
    purchase_id: str = ""
    verification_source: str = "app_store_or_play"
    artifact_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["receipt_or_token"] = "[redacted]"
        return payload


@dataclass(frozen=True)
class PurchaseVerificationResult:
    verification_state: str
    product_id: str
    platform: str
    purchase_id: str
    transaction_id: str = ""
    original_transaction_id: str = ""
    expires_at: str = ""
    started_at: str = ""
    last_verified_at: str = ""
    verification_message: str = ""
    purchase_token_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PurchaseRecord:
    app_user_id: str
    platform: str
    product_id: str
    purchase_id: str
    verification_state: str
    purchase_token_hash: str
    transaction_id: str = ""
    original_transaction_id: str = ""
    expires_at: str = ""
    started_at: str = ""
    last_verified_at: str = ""
    verification_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EntitlementSnapshot:
    app_user_id: str
    usage_count: int
    free_remaining: int
    free_analysis_limit: int
    subscription_status: str
    entitlement_state: str
    blocked_reason: str = ""
    active_product_id: str = ""
    purchase_verification_state: str = ""
    subscription_required_after_limit: bool = True
    support_contact_ref: str = ""
    privacy_policy_route_ref: str = ""
    terms_route_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnalysisAccessResult:
    allowed: bool
    blocked_reason: str
    entitlement: EntitlementSnapshot
    provider_gate_status: str = ""
    provider_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["entitlement"] = self.entitlement.to_dict()
        return payload


@dataclass(frozen=True)
class PurchaseRestoreResult:
    app_user_id: str
    restored_count: int
    entitlement: EntitlementSnapshot
    synced_purchase_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"entitlement": self.entitlement.to_dict()}
