from __future__ import annotations

import logging
import re
import time
from typing import Any
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response


LOGGER_NAME = "vibe_signal.backend.safe_request"
REQUEST_ID_HEADER = "X-Request-ID"
SAFE_REQUEST_ID_RE = re.compile(r"^req_[0-9a-f]{32}$")
BLOCKED_REQUEST_ID_RE = re.compile(
    r"secret|token|password|passwd|bearer|cookie|authorization|api[_-]?key|private|raw|message|chat|sk-",
    re.IGNORECASE,
)
SAFE_ENDPOINT_PATHS = {
    "/healthz",
    "/readyz",
    "/api/analyze",
    "/api/match",
    "/api/feedback",
    "/api/events/analysis",
    "/api/events/quota",
    "/api/events/billing",
    "/api/events/state",
    "/legal/privacy",
    "/legal/terms",
    "/legal/data-deletion",
    "/legal/data-export",
    "/legal/match-disclaimer",
}


def normalize_request_id(raw_value: str | None) -> str:
    candidate = str(raw_value or "").strip()
    if (
        candidate
        and SAFE_REQUEST_ID_RE.fullmatch(candidate)
        and not BLOCKED_REQUEST_ID_RE.search(candidate)
    ):
        return candidate
    return f"req_{uuid4().hex}"


def safe_log_path(path: str) -> str:
    candidate = str(path or "").strip()
    if candidate in SAFE_ENDPOINT_PATHS:
        return candidate
    if candidate.startswith("/api/events/"):
        return "/api/events/{event_type}"
    if candidate.startswith("/legal/"):
        return "/legal/{page}"
    return "unmatched_route"


def latency_bucket(latency_ms: float) -> str:
    if latency_ms < 100:
        return "lt_100ms"
    if latency_ms < 250:
        return "100_249ms"
    if latency_ms < 500:
        return "250_499ms"
    if latency_ms < 1000:
        return "500_999ms"
    return "gte_1000ms"


def status_category(status_code: int) -> str:
    if status_code >= 500:
        return "server_error"
    if status_code >= 400:
        return "client_error"
    return "success"


def build_safe_request_log_event(
    *,
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    latency_ms: float,
    error_category: str = "",
) -> dict[str, Any]:
    return {
        "event": "backend_request",
        "request_id": normalize_request_id(request_id),
        "method": str(method or "").upper(),
        "path": safe_log_path(path),
        "status_code": int(status_code),
        "status_category": status_category(int(status_code)),
        "latency_bucket": latency_bucket(float(latency_ms)),
        "error_category": str(error_category or ""),
        "raw_body_logged": False,
        "raw_message_logged": False,
        "provider_response_logged": False,
        "secrets_logged": False,
    }


class SafeRequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, logger_name: str = LOGGER_NAME) -> None:
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = time.perf_counter()
        request_id = normalize_request_id(None)
        status_code = 500
        error_category = ""
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        except Exception:
            error_category = "unhandled_exception"
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error.", "request_id": request_id},
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            latency_ms = (time.perf_counter() - started) * 1000
            event = build_safe_request_log_event(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                latency_ms=latency_ms,
                error_category=error_category,
            )
            self.logger.info("backend_request", extra={"safe_event": event})
