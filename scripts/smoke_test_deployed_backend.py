#!/usr/bin/env python3
"""Safe deployment smoke tests for a Vibe Signal backend host."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REQUEST_TIMEOUT_SECONDS = 10.0
MAX_RESPONSE_BYTES = 128_000
ALLOWED_BANDS = {"low", "mixed", "moderate", "strong"}
LEGAL_ENDPOINTS = (
    "/legal/privacy",
    "/legal/terms",
    "/legal/data-deletion",
    "/legal/data-export",
    "/legal/match-disclaimer",
)
EVENT_ENDPOINTS = (
    "/api/events/analysis",
    "/api/events/quota",
    "/api/events/billing",
    "/api/events/state",
)
SMOKE_ENDPOINTS = (
    "/healthz",
    "/readyz",
    *LEGAL_ENDPOINTS,
    "/api/match",
)
SYNTHETIC_MATCH_PAYLOAD: dict[str, Any] = {
    "conversation_id": "synthetic_deployment_smoke",
    "messages": [
        {
            "id": "m1",
            "author": "self",
            "text": "Can you confirm Tuesday at 10am?",
            "created_at": "2026-06-02T10:00:00Z",
        },
        {
            "id": "m2",
            "author": "other",
            "text": "Yes, Tuesday at 10am works. No pressure if we need to adjust.",
            "created_at": "2026-06-02T10:01:00Z",
        },
    ],
    "user_preferences": {
        "prefers_directness": True,
        "prefers_low_pressure": True,
        "prefers_explicit_plans": True,
        "max_message_load": "medium",
    },
}
SYNTHETIC_EVENT_PAYLOADS: dict[str, dict[str, Any]] = {
    "analysis": {
        "event_id": "evt_deployment_smoke_analysis",
        "client_timestamp": 1717322400000,
        "analysis_id": "analysis_deployment_smoke",
        "success": True,
        "mode": "local_analysis",
        "status": "analysis_completed",
        "event_origin": "deployment_smoke",
    },
    "quota": {
        "event_id": "evt_deployment_smoke_quota",
        "client_timestamp": 1717322400001,
        "type": "analysis_consumed",
        "remaining_after": 4,
        "analysis_id": "analysis_deployment_smoke",
    },
    "billing": {
        "event_id": "evt_deployment_smoke_billing",
        "client_timestamp": 1717322400002,
        "type": "entitlement_refresh",
        "status": "inactive",
        "product_id": "vibesignal_pro_monthly_ios",
        "entitlement_name": "vibesignal_pro",
        "event_origin": "deployment_smoke",
    },
    "state": {
        "event_id": "evt_deployment_smoke_state",
        "client_timestamp": 1717322400003,
        "premium_active": False,
        "remaining_uses": 5,
        "paywall_required": False,
        "current_period_type": "trial_week",
        "purchase_in_progress": False,
        "restore_in_progress": False,
    },
}
BLOCKED_USER_FACING_PHRASES = (
    "they lied",
    "they like you",
    "they cheated",
    "hidden intent",
    "diagnoses",
    "diagnosis",
    "neurotype",
    "attachment style",
    "emotional truth",
    "manipulating you",
)


@dataclass(frozen=True)
class TransportResponse:
    status_code: int
    headers: dict[str, str]
    body_text: str


@dataclass(frozen=True)
class SmokeResult:
    method: str
    path: str
    ok: bool
    status_code: int
    detail: str
    request_id_present: bool = False


Transport = Callable[[str, str, bytes | None, dict[str, str], float], TransportResponse]


def normalize_base_url(raw_value: str) -> str:
    value = str(raw_value or "").strip().rstrip("/")
    if not value:
        raise ValueError("base_url_required")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("base_url_must_be_http_or_https")
    if parsed.username or parsed.password:
        raise ValueError("base_url_must_not_include_credentials")
    if parsed.path not in {"", "/"} or parsed.params or parsed.query or parsed.fragment:
        raise ValueError("base_url_must_not_include_path_query_or_fragment")
    return f"{parsed.scheme}://{parsed.netloc}"


def smoke_request_for_path(path: str) -> tuple[str, bytes | None, dict[str, str]]:
    if path == "/api/match":
        body = json.dumps(SYNTHETIC_MATCH_PAYLOAD, separators=(",", ":")).encode("utf-8")
        return "POST", body, {"Content-Type": "application/json"}
    if path in EVENT_ENDPOINTS:
        event_type = path.rsplit("/", 1)[-1]
        body = json.dumps(SYNTHETIC_EVENT_PAYLOADS[event_type], separators=(",", ":")).encode("utf-8")
        return "POST", body, {"Content-Type": "application/json"}
    return "GET", None, {}


def default_transport(
    method: str,
    url: str,
    body: bytes | None,
    headers: dict[str, str],
    timeout: float,
) -> TransportResponse:
    request = Request(
        url,
        data=body,
        headers={
            **headers,
            "Accept": "application/json",
            "User-Agent": "vibe-signal-deployment-smoke/1",
        },
        method=method,
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - caller supplies deployment URL.
            text = response.read(MAX_RESPONSE_BYTES).decode("utf-8", errors="replace")
            return TransportResponse(
                status_code=int(response.status),
                headers={str(key).lower(): str(value) for key, value in response.headers.items()},
                body_text=text,
            )
    except HTTPError as exc:
        return TransportResponse(
            status_code=int(exc.code),
            headers={str(key).lower(): str(value) for key, value in exc.headers.items()},
            body_text="",
        )
    except URLError:
        return TransportResponse(status_code=0, headers={}, body_text="")


def parse_json_body(response: TransportResponse) -> tuple[dict[str, Any], str]:
    if not response.body_text:
        return {}, "empty_json_body"
    try:
        parsed = json.loads(response.body_text)
    except json.JSONDecodeError:
        return {}, "invalid_json_body"
    if not isinstance(parsed, dict):
        return {}, "json_body_must_be_object"
    return parsed, ""


def validate_healthz(payload: dict[str, Any]) -> str:
    if payload.get("status") != "ok":
        return "healthz_status_not_ok"
    if payload.get("service") != "vibe-signal-backend":
        return "healthz_service_mismatch"
    return ""


def validate_readyz(payload: dict[str, Any]) -> str:
    if payload.get("status") != "ready":
        return "readyz_status_not_ready"
    checks = payload.get("checks")
    if not isinstance(checks, dict):
        return "readyz_checks_missing"
    expected_false_flags = (
        "raw_message_persistence_enabled",
        "raw_message_logging_enabled",
        "analytics_tracking_enabled",
        "training_enabled",
    )
    if any(checks.get(flag) is not False for flag in expected_false_flags):
        return "readyz_unsafe_flag_enabled"
    if checks.get("safe_request_logging_enabled") is not True:
        return "readyz_safe_request_logging_disabled"
    if checks.get("deterministic_routes_registered") is not True:
        return "readyz_routes_not_registered"
    return ""


def validate_legal_page(payload: dict[str, Any]) -> str:
    if payload.get("status") != "draft_requires_legal_review":
        return "legal_status_mismatch"
    if payload.get("not_legal_advice") is not True:
        return "legal_not_legal_advice_missing"
    if payload.get("closed_beta_only") is not True:
        return "legal_closed_beta_flag_missing"
    if payload.get("production_compliance_claimed") is not False:
        return "legal_production_compliance_overclaim"
    if not payload.get("document_ref"):
        return "legal_document_ref_missing"
    if not isinstance(payload.get("sections"), list) or not payload["sections"]:
        return "legal_sections_missing"
    return ""


def validate_match(payload: dict[str, Any]) -> str:
    if payload.get("conversation_id") != SYNTHETIC_MATCH_PAYLOAD["conversation_id"]:
        return "match_conversation_id_mismatch"
    if payload.get("redline_status") != "allow":
        return "match_redline_not_allow"
    if payload.get("compatibility_band") not in ALLOWED_BANDS:
        return "match_band_invalid"
    score = payload.get("score")
    if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0.0 <= float(score) <= 1.0:
        return "match_score_invalid"
    if not isinstance(payload.get("positive_factors"), list):
        return "match_positive_factors_missing"
    if not isinstance(payload.get("risk_factors"), list):
        return "match_risk_factors_missing"
    if not isinstance(payload.get("evidence"), list):
        return "match_evidence_missing"
    if not isinstance(payload.get("safe_summary"), str) or not payload["safe_summary"].strip():
        return "match_safe_summary_missing"
    if not isinstance(payload.get("safe_explanation"), str) or not payload["safe_explanation"].strip():
        return "match_safe_explanation_missing"
    user_facing_values = [
        str(payload.get("safe_summary", "")),
        str(payload.get("safe_explanation", "")),
        *(str(item) for item in payload.get("positive_factors", []) if isinstance(item, str)),
        *(str(item) for item in payload.get("risk_factors", []) if isinstance(item, str)),
    ]
    for item in payload.get("evidence", []):
        if isinstance(item, dict):
            user_facing_values.append(str(item.get("safe_phrase", "")))
            user_facing_values.append(str(item.get("explanation", "")))
    combined = " ".join(user_facing_values).lower()
    if any(phrase in combined for phrase in BLOCKED_USER_FACING_PHRASES):
        return "match_unsafe_user_facing_claim"
    return ""


def validate_event(path: str, payload: dict[str, Any]) -> str:
    expected_type = path.rsplit("/", 1)[-1]
    if payload.get("status") != "accepted":
        return "event_status_not_accepted"
    if payload.get("event_type") != expected_type:
        return "event_type_mismatch"
    if payload.get("raw_payload_persisted") is not False:
        return "event_raw_payload_persisted"
    stored_event = payload.get("stored_event")
    if not isinstance(stored_event, dict):
        return "event_stored_metadata_missing"
    if stored_event.get("event_type") != expected_type:
        return "event_stored_type_mismatch"
    return ""


def validation_error_for_path(path: str, payload: dict[str, Any]) -> str:
    if path == "/healthz":
        return validate_healthz(payload)
    if path == "/readyz":
        return validate_readyz(payload)
    if path in LEGAL_ENDPOINTS:
        return validate_legal_page(payload)
    if path == "/api/match":
        return validate_match(payload)
    if path in EVENT_ENDPOINTS:
        return validate_event(path, payload)
    return "unsupported_smoke_endpoint"


def run_smoke_checks(
    base_url: str,
    *,
    transport: Transport = default_transport,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
    include_events: bool = False,
) -> list[SmokeResult]:
    normalized_base_url = normalize_base_url(base_url)
    results: list[SmokeResult] = []
    endpoints = (*SMOKE_ENDPOINTS, *EVENT_ENDPOINTS) if include_events else SMOKE_ENDPOINTS
    for path in endpoints:
        method, body, headers = smoke_request_for_path(path)
        response = transport(method, f"{normalized_base_url}{path}", body, headers, timeout)
        request_id_present = bool(response.headers.get("x-request-id"))
        if response.status_code != 200:
            results.append(
                SmokeResult(
                    method=method,
                    path=path,
                    ok=False,
                    status_code=response.status_code,
                    detail="unexpected_status",
                    request_id_present=request_id_present,
                )
            )
            continue
        if not request_id_present:
            results.append(
                SmokeResult(
                    method=method,
                    path=path,
                    ok=False,
                    status_code=response.status_code,
                    detail="request_id_missing",
                    request_id_present=False,
                )
            )
            continue
        payload, parse_error = parse_json_body(response)
        if parse_error:
            results.append(
                SmokeResult(method, path, False, response.status_code, parse_error, request_id_present)
            )
            continue
        validation_error = validation_error_for_path(path, payload)
        results.append(
            SmokeResult(
                method=method,
                path=path,
                ok=not validation_error,
                status_code=response.status_code,
                detail=validation_error or "ok",
                request_id_present=request_id_present,
            )
        )
    return results


def print_summary(results: list[SmokeResult]) -> None:
    for result in results:
        label = "PASS" if result.ok else "FAIL"
        request_id = "yes" if result.request_id_present else "no"
        print(
            f"[{label}] {result.method} {result.path} "
            f"status={result.status_code} request_id={request_id} detail={result.detail}"
        )
    passed = sum(1 for result in results if result.ok)
    print(f"Summary: {passed}/{len(results)} deployment smoke checks passed.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run safe Vibe Signal backend deployment smoke tests.")
    parser.add_argument("--base-url", required=True, help="Backend base URL, for example https://example.invalid")
    parser.add_argument("--timeout", type=float, default=REQUEST_TIMEOUT_SECONDS)
    parser.add_argument(
        "--include-events",
        action="store_true",
        help="Also smoke-test bounded metadata event routes when mobile event logging is in scope.",
    )
    args = parser.parse_args(argv)

    try:
        results = run_smoke_checks(args.base_url, timeout=args.timeout, include_events=args.include_events)
    except ValueError as exc:
        print(f"[FAIL] invalid base url: {exc}", file=sys.stderr)
        return 2

    print_summary(results)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
