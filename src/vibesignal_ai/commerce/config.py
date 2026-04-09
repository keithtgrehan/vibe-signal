"""Static commerce configuration for the sellable app path."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FREE_ANALYSIS_LIMIT = 10
SUBSCRIPTION_REQUIRED_AFTER_LIMIT = True
SUBSCRIPTION_PRICE_DISPLAY = "€1.89/month"

IOS_MONTHLY_PRODUCT_ID = "vibesignal_pro_monthly_ios"
PLAY_MONTHLY_PRODUCT_ID = "vibesignal_pro_monthly_android"

SUPPORT_CONTACT_REF = "support-contact-placeholder"
PRIVACY_POLICY_ROUTE_REF = "/legal/privacy-policy"
TERMS_ROUTE_REF = "/legal/terms"

DEFAULT_STATE_DB_FILENAME = "commerce_state.sqlite3"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_state_db_path() -> Path:
    return repo_root() / "app" / "state" / DEFAULT_STATE_DB_FILENAME


@dataclass(frozen=True)
class CommerceConfig:
    state_db_path: Path = default_state_db_path()
    free_analysis_limit: int = FREE_ANALYSIS_LIMIT
    subscription_required_after_limit: bool = SUBSCRIPTION_REQUIRED_AFTER_LIMIT
    subscription_price_display: str = SUBSCRIPTION_PRICE_DISPLAY
    ios_monthly_product_id: str = IOS_MONTHLY_PRODUCT_ID
    play_monthly_product_id: str = PLAY_MONTHLY_PRODUCT_ID
    support_contact_ref: str = SUPPORT_CONTACT_REF
    privacy_policy_route_ref: str = PRIVACY_POLICY_ROUTE_REF
    terms_route_ref: str = TERMS_ROUTE_REF
