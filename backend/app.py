from __future__ import annotations

import logging
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import BackendSettings, load_backend_settings, safe_version_label
from .monitoring import LOGGER_NAME, SafeRequestLoggingMiddleware
from .routes import analyze, events, feedback, legal, match


def _readiness_payload(app: FastAPI) -> dict[str, object]:
    settings: BackendSettings = app.state.backend_settings
    route_paths = {route.path for route in app.routes}
    deterministic_routes_registered = all(
        path in route_paths
        for path in (
            "/healthz",
            "/api/analyze",
            "/api/match",
            "/api/feedback",
            "/api/events/analysis",
            "/api/events/quota",
            "/api/events/billing",
            "/api/events/state",
        )
    )
    checks = {
        "deterministic_routes_registered": deterministic_routes_registered,
        "cors_allowed_origins_count": len(settings.allowed_origins),
        "raw_message_persistence_enabled": settings.raw_message_persistence_enabled,
        "raw_message_logging_enabled": settings.raw_message_logging_enabled,
        "safe_request_logging_enabled": settings.safe_request_logging_enabled,
        "analytics_tracking_enabled": settings.analytics_tracking_enabled,
        "training_enabled": settings.training_enabled,
    }
    unsafe_enabled = any(
        (
            settings.raw_message_persistence_enabled,
            settings.raw_message_logging_enabled,
            settings.analytics_tracking_enabled,
            settings.training_enabled,
        )
    )
    return {
        "status": "ready" if deterministic_routes_registered and not unsafe_enabled else "not_ready",
        "service": "vibe-signal-backend",
        "environment": settings.environment,
        "version": safe_version_label(settings.version),
        "log_level": settings.log_level,
        "checks": checks,
        "config_warnings": list(settings.config_warnings),
        "deployment_claim": "readiness metadata only; no production compliance claim.",
    }


def create_app(settings: BackendSettings | None = None) -> FastAPI:
    resolved_settings = settings or load_backend_settings()
    backend_app = FastAPI(
        title="VibeSignal Backend",
        version=safe_version_label(resolved_settings.version),
    )
    backend_app.state.backend_settings = resolved_settings
    logging.getLogger(LOGGER_NAME).setLevel(resolved_settings.log_level)

    @backend_app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _request: Request,
        _exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid request payload."},
        )

    if resolved_settings.safe_request_logging_enabled:
        backend_app.add_middleware(SafeRequestLoggingMiddleware)

    if resolved_settings.allowed_origins:
        backend_app.add_middleware(
            CORSMiddleware,
            allow_origins=list(resolved_settings.allowed_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type"],
        )

    @backend_app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "service": "vibe-signal-backend"}

    @backend_app.get("/readyz")
    def readyz() -> dict[str, object]:
        return _readiness_payload(backend_app)

    @backend_app.get("/api/status")
    def api_status() -> dict[str, object]:
        settings: BackendSettings = backend_app.state.backend_settings
        return {
            "ok": True,
            "service": "vibe-signal-backend",
            "version": safe_version_label(settings.version),
            "environment": settings.environment,
            "timestamp": datetime.now(UTC).isoformat(),
            "raw_message_persistence_enabled": settings.raw_message_persistence_enabled,
            "raw_message_logging_enabled": settings.raw_message_logging_enabled,
            "analytics_tracking_enabled": settings.analytics_tracking_enabled,
            "training_enabled": settings.training_enabled,
        }

    backend_app.include_router(analyze.router)
    backend_app.include_router(match.router)
    backend_app.include_router(feedback.router)
    backend_app.include_router(events.router)
    backend_app.include_router(legal.router)
    return backend_app


app = create_app()
