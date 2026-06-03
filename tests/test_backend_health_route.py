from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app, create_app
from backend.config import load_backend_settings


def test_health_route_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "vibe-signal-backend"}


def test_api_status_route_returns_safe_metadata_only() -> None:
    client = TestClient(app)

    response = client.get("/api/status")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["service"] == "vibe-signal-backend"
    assert body["version"]
    assert body["environment"] in {"local", "development", "staging", "production", "test", "unknown"}
    assert body["timestamp"]
    assert body["raw_message_persistence_enabled"] is False
    assert body["raw_message_logging_enabled"] is False
    assert body["analytics_tracking_enabled"] is False
    assert body["training_enabled"] is False


def test_api_status_route_includes_configured_safe_deploy_metadata(monkeypatch) -> None:
    monkeypatch.setenv("GIT_COMMIT", "abc123def456")
    monkeypatch.setenv("DEPLOY_VERSION", "closed-beta-rc1")
    monkeypatch.setenv("BUILD_TIMESTAMP", "2026-06-03T12:34:56Z")
    monkeypatch.setenv("SERVICE_REVISION", "render-revision-42")
    client = TestClient(create_app(load_backend_settings()))

    response = client.get("/api/status")

    assert response.status_code == 200
    body = response.json()
    assert body["git_commit"] == "abc123def456"
    assert body["deploy_version"] == "closed-beta-rc1"
    assert body["build_timestamp"] == "2026-06-03T12:34:56Z"
    assert body["service_revision"] == "render-revision-42"


def test_api_status_route_uses_unknown_for_missing_deploy_metadata(
    monkeypatch,
) -> None:
    for env_name in (
        "GIT_COMMIT",
        "RENDER_GIT_COMMIT",
        "VERCEL_GIT_COMMIT_SHA",
        "DEPLOY_VERSION",
        "BUILD_TIMESTAMP",
        "SERVICE_REVISION",
        "RENDER_SERVICE_ID",
        "RENDER_SERVICE_NAME",
    ):
        monkeypatch.delenv(env_name, raising=False)
    client = TestClient(create_app(load_backend_settings()))

    response = client.get("/api/status")

    assert response.status_code == 200
    body = response.json()
    assert body["git_commit"] == "unknown"
    assert body["deploy_version"] == "unknown"
    assert body["build_timestamp"] == "unknown"
    assert body["service_revision"] == "unknown"


def test_api_status_route_does_not_expose_arbitrary_environment(
    monkeypatch,
) -> None:
    monkeypatch.setenv("GIT_COMMIT", "abc123def456")
    monkeypatch.setenv("SECRET_TOKEN", "secret-token-should-not-leak")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:password@example.invalid/db")
    monkeypatch.setenv("INTERNAL_PATH", "/Users/tester/private")
    client = TestClient(create_app(load_backend_settings()))

    response = client.get("/api/status")

    assert response.status_code == 200
    body = response.json()
    body_text = response.text
    assert "SECRET_TOKEN" not in body
    assert "DATABASE_URL" not in body
    assert "INTERNAL_PATH" not in body
    assert "secret-token-should-not-leak" not in body_text
    assert "postgres://" not in body_text
    assert "/Users/tester/private" not in body_text
