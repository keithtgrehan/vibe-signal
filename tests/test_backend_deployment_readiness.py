from __future__ import annotations

import json

from fastapi.testclient import TestClient

from backend.app import app, create_app
from backend.config import BackendSettings, load_backend_settings


def test_readyz_exposes_deployment_safe_flags() -> None:
    client = TestClient(app)

    response = client.get("/readyz")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "vibe-signal-backend"
    assert body["status"] == "ready"
    assert body["log_level"] == "INFO"
    assert body["deployment_claim"] == "readiness metadata only; no production compliance claim."
    assert body["checks"]["raw_message_persistence_enabled"] is False
    assert body["checks"]["raw_message_logging_enabled"] is False
    assert body["checks"]["analytics_tracking_enabled"] is False
    assert body["checks"]["training_enabled"] is False
    assert body["checks"]["deterministic_routes_registered"] is True


def test_backend_settings_parse_safe_cors_origins_and_warn_on_rejected_values() -> None:
    settings = load_backend_settings(
        {
            "VIBE_BACKEND_ENV": "production",
            "VIBE_BACKEND_VERSION": "2026.06.02",
            "VIBE_BACKEND_ALLOWED_ORIGINS": "https://app.example.com, http://localhost:19006, *, ftp://bad.example",
            "VIBE_BACKEND_LOG_LEVEL": "debug",
        }
    )

    assert settings.environment == "production"
    assert settings.version == "2026.06.02"
    assert settings.log_level == "DEBUG"
    assert settings.allowed_origins == ("https://app.example.com", "http://localhost:19006")
    assert "wildcard_origin_rejected" in settings.config_warnings
    assert "unsupported_origin_scheme_rejected" in settings.config_warnings
    assert settings.raw_message_persistence_enabled is False
    assert settings.raw_message_logging_enabled is False
    assert settings.analytics_tracking_enabled is False
    assert settings.training_enabled is False


def test_backend_settings_rejects_path_query_fragment_and_unknown_environment() -> None:
    settings = load_backend_settings(
        {
            "VIBE_BACKEND_ENV": "mystery-prod",
            "VIBE_BACKEND_ALLOWED_ORIGINS": (
                "https://app.example.com/path,"
                "https://admin.example.com?debug=true,"
                "https://mobile.example.com#fragment,"
                "https://safe.example.com"
            ),
            "VIBE_BACKEND_LOG_LEVEL": "verbose",
        }
    )

    assert settings.environment == "local"
    assert settings.log_level == "INFO"
    assert settings.allowed_origins == ("https://safe.example.com",)
    assert "unsupported_environment_defaulted_to_local" in settings.config_warnings
    assert "unsupported_log_level_defaulted_to_info" in settings.config_warnings
    assert "origin_must_not_include_path_query_or_fragment" in settings.config_warnings


def test_readyz_reports_cors_count_without_echoing_origin_values() -> None:
    configured_app = create_app(
        BackendSettings(
            allowed_origins=("https://private-mobile.example.com",),
            environment="production",
            version="test",
        )
    )
    client = TestClient(configured_app)

    response = client.get("/readyz")

    assert response.status_code == 200
    body = response.json()
    assert body["checks"]["cors_allowed_origins_count"] == 1
    assert "https://private-mobile.example.com" not in json.dumps(body)


def test_configured_cors_allows_only_exact_origins() -> None:
    configured_app = create_app(
        BackendSettings(
            allowed_origins=("https://mobile.example.com",),
            environment="staging",
            version="test",
        )
    )
    client = TestClient(configured_app)

    allowed = client.options(
        "/api/match",
        headers={
            "Origin": "https://mobile.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    blocked = client.options(
        "/api/match",
        headers={
            "Origin": "https://other.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.headers["access-control-allow-origin"] == "https://mobile.example.com"
    assert "access-control-allow-origin" not in blocked.headers
