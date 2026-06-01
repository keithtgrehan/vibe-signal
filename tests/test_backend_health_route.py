from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app


def test_health_route_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "vibe-signal-backend"}
