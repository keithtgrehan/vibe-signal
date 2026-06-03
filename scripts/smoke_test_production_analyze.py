#!/usr/bin/env python3
"""Metadata-only production smoke check for the hosted analyze path."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REQUEST_TIMEOUT_SECONDS = 30.0
MAX_RESPONSE_BYTES = 128_000
SAFE_REQUEST_ID_RE = re.compile(r"^req_[0-9a-f]{32}$")
SMOKE_ENDPOINTS = ("/healthz", "/api/status", "/api/analyze")
SYNTHETIC_ANALYZE_PAYLOAD: dict[str, Any] = {
    "conversation_id": "synthetic_production_analyze_smoke",
    "text": "self: Are we still on for Friday?\nother: maybe later, not sure yet",
}
BLOCKED_USER_FACING_PHRASES = (
    "detect cheating",
    "cheating detector",
    "they like you",
    "hidden intent",
    "diagnose",
    "diagnosis",
    "narcissist",
    "attachment style",
    "adhd",
    "autism",
    "manipulate",
    "make them",
    "win them back",
    "guaranteed",
    "this proves",
    "emotional truth",
    "validated accuracy",
    "production-grade",
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
    request_id: str = "unsafe_or_missing"


Transport = Callable[[str, str, bytes | None, dict[str, str], float], TransportResponse]


def normalize_base_url(raw_value: str) -> str:
    value = str(raw_value or "").strip().rstrip("/")
    if not value:
        raise ValueError("base_url_required")
    if any(character.isspace() for character in value):
        raise ValueError("base_url_must_not_include_whitespace")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("base_url_must_be_http_or_https")
    if parsed.username or parsed.password:
        raise ValueError("base_url_must_not_include_credentials")
    if parsed.path not in {"", "/"} or parsed.params or parsed.query or parsed.fragment:
        raise ValueError("base_url_must_not_include_path_query_or_fragment")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("base_url_must_include_valid_port") from exc
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("base_url_must_include_valid_port")
    return f"{parsed.scheme}://{parsed.netloc}"


def normalize_timeout(raw_value: float) -> float:
    timeout = float(raw_value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout_must_be_positive")
    return timeout


def normalize_retries(raw_value: int) -> int:
    retries = int(raw_value)
    if retries < 1 or retries > 5:
        raise ValueError("retries_must_be_between_1_and_5")
    return retries


def normalize_retry_delay_seconds(raw_value: float) -> float:
    delay = float(raw_value)
    if not math.isfinite(delay) or delay < 0 or delay > 30:
        raise ValueError("retry_delay_seconds_must_be_between_0_and_30")
    return delay


def smoke_request_for_path(path: str) -> tuple[str, bytes | None, dict[str, str]]:
    if path == "/api/analyze":
        body = json.dumps(SYNTHETIC_ANALYZE_PAYLOAD, separators=(",", ":")).encode("utf-8")
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
            "User-Agent": "vibe-signal-production-analyze-smoke/1",
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
    except (URLError, TimeoutError, OSError, ValueError):
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


def validate_status(payload: dict[str, Any]) -> str:
    if payload.get("ok") is not True:
        return "status_ok_not_true"
    if payload.get("service") != "vibe-signal-backend":
        return "status_service_mismatch"
    expected_false_flags = (
        "raw_message_persistence_enabled",
        "raw_message_logging_enabled",
        "analytics_tracking_enabled",
        "training_enabled",
    )
    if any(payload.get(flag) is not False for flag in expected_false_flags):
        return "status_unsafe_flag_enabled"
    return ""


def _user_facing_values(payload: dict[str, Any]) -> list[str]:
    values = [str(payload.get("safe_summary", ""))]
    values.extend(str(item) for item in payload.get("cannot_infer", []) if isinstance(item, str))
    for item in payload.get("evidence", []):
        if isinstance(item, dict):
            values.append(str(item.get("safe_phrase", "")))
            values.append(str(item.get("explanation", "")))
    return values


def validate_analyze(payload: dict[str, Any]) -> str:
    if payload.get("conversation_id") != SYNTHETIC_ANALYZE_PAYLOAD["conversation_id"]:
        return "analyze_conversation_id_mismatch"
    if payload.get("analysis_mode") != "deterministic_local_only":
        return "analyze_mode_mismatch"
    if payload.get("provider_used") is not False:
        return "analyze_provider_used"
    if payload.get("raw_chat_persisted") is not False:
        return "analyze_raw_chat_persisted"
    if not isinstance(payload.get("evidence"), list):
        return "analyze_evidence_missing"
    combined = " ".join(_user_facing_values(payload)).lower()
    if any(phrase in combined for phrase in BLOCKED_USER_FACING_PHRASES):
        return "analyze_unsafe_user_facing_claim"
    return ""


def validation_error_for_path(path: str, payload: dict[str, Any]) -> str:
    if path == "/healthz":
        return validate_healthz(payload)
    if path == "/api/status":
        return validate_status(payload)
    if path == "/api/analyze":
        return validate_analyze(payload)
    return "unsupported_smoke_endpoint"


def safe_request_id(value: str) -> str:
    candidate = str(value or "").strip()
    if SAFE_REQUEST_ID_RE.fullmatch(candidate):
        return candidate
    return "unsafe_or_missing"


def run_smoke_checks(
    base_url: str,
    *,
    transport: Transport = default_transport,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
    retries: int = 2,
    retry_delay_seconds: float = 1.0,
) -> list[SmokeResult]:
    normalized_base_url = normalize_base_url(base_url)
    normalized_timeout = normalize_timeout(timeout)
    normalized_retries = normalize_retries(retries)
    normalized_retry_delay_seconds = normalize_retry_delay_seconds(retry_delay_seconds)
    results: list[SmokeResult] = []
    for path in SMOKE_ENDPOINTS:
        result: SmokeResult | None = None
        for attempt in range(normalized_retries):
            method, body, headers = smoke_request_for_path(path)
            response = transport(method, f"{normalized_base_url}{path}", body, headers, normalized_timeout)
            request_id = safe_request_id(response.headers.get("x-request-id", ""))
            if response.status_code != 200:
                detail = "transport_error" if response.status_code == 0 else "unexpected_status"
                result = SmokeResult(method, path, False, response.status_code, detail, request_id)
            elif request_id == "unsafe_or_missing":
                result = SmokeResult(method, path, False, response.status_code, "request_id_missing", request_id)
            else:
                payload, parse_error = parse_json_body(response)
                if parse_error:
                    result = SmokeResult(method, path, False, response.status_code, parse_error, request_id)
                else:
                    validation_error = validation_error_for_path(path, payload)
                    result = SmokeResult(
                        method,
                        path,
                        not validation_error,
                        response.status_code,
                        validation_error or "ok",
                        request_id,
                    )
            if result.ok or attempt + 1 == normalized_retries:
                break
            if normalized_retry_delay_seconds:
                time.sleep(normalized_retry_delay_seconds)
        if result is None:
            raise RuntimeError("smoke_result_missing")
        results.append(result)
    return results


def print_summary(results: list[SmokeResult]) -> None:
    for result in results:
        label = "PASS" if result.ok else "FAIL"
        print(
            f"[{label}] {result.method} {result.path} "
            f"status={result.status_code} request_id={result.request_id} detail={result.detail}"
        )
    passed = sum(1 for result in results if result.ok)
    print(f"Summary: {passed}/{len(results)} production analyze smoke checks passed.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run safe production analyze smoke checks.")
    parser.add_argument("--base-url", required=True, help="Backend base URL, for example https://example.invalid")
    parser.add_argument("--timeout", type=float, default=REQUEST_TIMEOUT_SECONDS)
    parser.add_argument("--retries", type=int, default=2, help="Bounded attempts for cold Render starts.")
    parser.add_argument("--retry-delay-seconds", type=float, default=1.0)
    args = parser.parse_args(argv)

    try:
        results = run_smoke_checks(
            args.base_url,
            timeout=args.timeout,
            retries=args.retries,
            retry_delay_seconds=args.retry_delay_seconds,
        )
    except ValueError as exc:
        print(f"[FAIL] invalid smoke-test argument: {exc}", file=sys.stderr)
        return 2

    print_summary(results)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
