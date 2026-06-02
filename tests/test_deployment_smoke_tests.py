from __future__ import annotations

import json
from urllib.parse import urlparse

import pytest

from scripts import smoke_test_deployed_backend as smoke


REQUEST_ID = "req_abcdef1234567890abcdef1234567890"


def fake_success_transport(
    method: str,
    url: str,
    body: bytes | None,
    headers: dict[str, str],
    timeout: float,
) -> smoke.TransportResponse:
    path = urlparse(url).path
    assert timeout > 0
    if path == "/api/match":
        assert method == "POST"
        assert headers["Content-Type"] == "application/json"
        assert body is not None
        assert json.loads(body.decode("utf-8")) == smoke.SYNTHETIC_MATCH_PAYLOAD
        payload = {
            "conversation_id": "synthetic_deployment_smoke",
            "compatibility_band": "moderate",
            "score": 0.74,
            "positive_factors": ["clear confirmation"],
            "risk_factors": [],
            "evidence": [{"evidence_id": "ev_1", "safe_phrase": "message contains clear timing"}],
            "safe_summary": "The exchange shows observable fit on directness and low-pressure wording.",
            "safe_explanation": "The smoke test uses synthetic text and verifies the response shape only.",
            "redline_status": "allow",
        }
        return smoke.TransportResponse(200, {"x-request-id": REQUEST_ID}, json.dumps(payload))
    if path in smoke.EVENT_ENDPOINTS:
        event_type = path.rsplit("/", 1)[-1]
        assert method == "POST"
        assert headers["Content-Type"] == "application/json"
        assert body is not None
        assert json.loads(body.decode("utf-8")) == smoke.SYNTHETIC_EVENT_PAYLOADS[event_type]
        payload = {
            "status": "accepted",
            "event_type": event_type,
            "raw_payload_persisted": False,
            "stored_event": {
                "event_id": f"evt_deployment_smoke_{event_type}",
                "event_type": event_type,
            },
        }
        return smoke.TransportResponse(200, {"x-request-id": REQUEST_ID}, json.dumps(payload))
    if path == "/healthz":
        assert method == "GET"
        return smoke.TransportResponse(
            200,
            {"x-request-id": REQUEST_ID},
            json.dumps({"status": "ok", "service": "vibe-signal-backend"}),
        )
    if path == "/readyz":
        payload = {
            "status": "ready",
            "checks": {
                "raw_message_persistence_enabled": False,
                "raw_message_logging_enabled": False,
                "analytics_tracking_enabled": False,
                "training_enabled": False,
                "safe_request_logging_enabled": True,
                "deterministic_routes_registered": True,
            },
        }
        return smoke.TransportResponse(200, {"x-request-id": REQUEST_ID}, json.dumps(payload))
    if path in smoke.LEGAL_ENDPOINTS:
        payload = {
            "status": "draft_requires_legal_review",
            "not_legal_advice": True,
            "closed_beta_only": True,
            "production_compliance_claimed": False,
            "document_ref": f"docs/{path.rsplit('/', 1)[-1]}.md",
            "sections": ["Draft closed-beta readiness copy."],
        }
        return smoke.TransportResponse(200, {"x-request-id": REQUEST_ID}, json.dumps(payload))
    return smoke.TransportResponse(404, {"x-request-id": REQUEST_ID}, "")


def test_smoke_endpoint_list_covers_backend_pre_beta_routes() -> None:
    assert smoke.SMOKE_ENDPOINTS == (
        "/healthz",
        "/readyz",
        "/legal/privacy",
        "/legal/terms",
        "/legal/data-deletion",
        "/legal/data-export",
        "/legal/match-disclaimer",
        "/api/match",
    )


@pytest.mark.parametrize(
    "raw_url,expected",
    [
        ("https://api.example.test", "https://api.example.test"),
        ("https://api.example.test/", "https://api.example.test"),
        ("http://127.0.0.1:8000", "http://127.0.0.1:8000"),
    ],
)
def test_normalize_base_url_accepts_safe_http_urls(raw_url: str, expected: str) -> None:
    assert smoke.normalize_base_url(raw_url) == expected


@pytest.mark.parametrize(
    "raw_url",
    [
        "",
        "ftp://api.example.test",
        "https://user:pass@example.test",
        "https://api.example.test/path",
        "https://api.example.test?debug=true",
        "https://api.example.test#fragment",
    ],
)
def test_normalize_base_url_rejects_unsafe_or_route_urls(raw_url: str) -> None:
    with pytest.raises(ValueError):
        smoke.normalize_base_url(raw_url)


def test_synthetic_match_payload_uses_only_toy_content() -> None:
    serialized = json.dumps(
        {
            "match": smoke.SYNTHETIC_MATCH_PAYLOAD,
            "events": smoke.SYNTHETIC_EVENT_PAYLOADS,
        }
    ).lower()
    assert "synthetic_deployment_smoke" in serialized
    for blocked in (
        "password",
        "api_key",
        "bearer",
        "third-party",
        "private chat",
        "medical data",
        "financial data",
    ):
        assert blocked not in serialized


def test_run_smoke_checks_passes_with_safe_fake_transport() -> None:
    results = smoke.run_smoke_checks(
        "https://api.example.test",
        transport=fake_success_transport,
    )

    assert len(results) == len(smoke.SMOKE_ENDPOINTS)
    assert all(result.ok for result in results)
    assert all(result.request_id_present for result in results)


def test_run_smoke_checks_can_include_bounded_event_routes() -> None:
    results = smoke.run_smoke_checks(
        "https://api.example.test",
        transport=fake_success_transport,
        include_events=True,
    )

    assert [result.path for result in results] == [*smoke.SMOKE_ENDPOINTS, *smoke.EVENT_ENDPOINTS]
    assert all(result.ok for result in results)


def test_run_smoke_checks_fails_when_request_id_is_missing() -> None:
    def missing_request_id_transport(
        method: str,
        url: str,
        body: bytes | None,
        headers: dict[str, str],
        timeout: float,
    ) -> smoke.TransportResponse:
        response = fake_success_transport(method, url, body, headers, timeout)
        return smoke.TransportResponse(response.status_code, {}, response.body_text)

    results = smoke.run_smoke_checks(
        "https://api.example.test",
        transport=missing_request_id_transport,
    )

    assert results
    assert not any(result.ok for result in results)
    assert {result.detail for result in results} == {"request_id_missing"}


def test_match_response_user_facing_text_blocks_unsafe_claims() -> None:
    payload = {
        "conversation_id": "synthetic_deployment_smoke",
        "compatibility_band": "moderate",
        "score": 0.5,
        "positive_factors": [],
        "risk_factors": [],
        "evidence": [],
        "safe_summary": "This says they lied.",
        "safe_explanation": "Synthetic response fixture.",
        "redline_status": "allow",
    }

    assert smoke.validate_match(payload) == "match_unsafe_user_facing_claim"


def test_run_smoke_checks_returns_failure_without_printing_body() -> None:
    def failing_transport(
        _method: str,
        _url: str,
        _body: bytes | None,
        _headers: dict[str, str],
        _timeout: float,
    ) -> smoke.TransportResponse:
        return smoke.TransportResponse(500, {"x-request-id": REQUEST_ID}, "unexpected backend body")

    results = smoke.run_smoke_checks(
        "https://api.example.test",
        transport=failing_transport,
    )

    assert results
    assert not any(result.ok for result in results)
    assert {result.detail for result in results} == {"unexpected_status"}
    assert "unexpected backend body" not in json.dumps([result.__dict__ for result in results])


def test_main_returns_nonzero_when_any_check_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        smoke,
        "run_smoke_checks",
        lambda *_args, **_kwargs: [
            smoke.SmokeResult("GET", "/healthz", False, 500, "unexpected_status", True)
        ],
    )

    exit_code = smoke.main(["--base-url", "https://api.example.test"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "[FAIL] GET /healthz status=500" in captured.out
    assert "unexpected backend body" not in captured.out


def test_main_include_events_runs_event_endpoints(monkeypatch, capsys) -> None:
    captured_include_events = {}

    def fake_run_smoke_checks(*_args, **kwargs):
        captured_include_events["value"] = kwargs.get("include_events")
        return [smoke.SmokeResult("GET", "/healthz", True, 200, "ok", True)]

    monkeypatch.setattr(smoke, "run_smoke_checks", fake_run_smoke_checks)

    exit_code = smoke.main(["--base-url", "https://api.example.test", "--include-events"])

    assert exit_code == 0
    assert captured_include_events["value"] is True
    assert "Summary: 1/1 deployment smoke checks passed." in capsys.readouterr().out


def test_main_rejects_invalid_base_url(capsys) -> None:
    exit_code = smoke.main(["--base-url", "https://api.example.test/path"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "invalid base url" in captured.err
