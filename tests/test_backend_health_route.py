from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app


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
