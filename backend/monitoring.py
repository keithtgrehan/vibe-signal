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
SAFE_REQUEST_ID_RE = re.compile(
    r"^(?:req|trace|smoke|closed-beta)[A-Za-z0-9_.:-]{0,72}$"
    r"|^[0-9a-fA-F]{32}$"
    r"|^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def normalize_request_id(raw_value: str | None) -> str:
    candidate = str(raw_value or "").strip()
    if candidate and SAFE_REQUEST_ID_RE.fullmatch(candidate):
        return candidate
    return uuid4().hex


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
        "path": str(path or ""),
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
        request_id = normalize_request_id(request.headers.get(REQUEST_ID_HEADER))
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
