from __future__ import annotations

import logging

from fastapi.testclient import TestClient

import backend.routes.match as match_route
from backend.app import create_app
from backend.config import BackendSettings
from backend.monitoring import build_safe_request_log_event, normalize_request_id
from backend.storage import EVENT_ROWS, FEEDBACK_ROWS


LOGGER_NAME = "vibe_signal.backend.safe_request"


def logged_safe_events(caplog) -> list[dict[str, object]]:
    return [
        record.safe_event
        for record in caplog.records
        if hasattr(record, "safe_event") and record.name == LOGGER_NAME
    ]


def test_safe_request_log_event_contains_only_metadata() -> None:
    event = build_safe_request_log_event(
        request_id="req_abcdef1234567890abcdef1234567890",
        method="post",
        path="/api/match",
        status_code=200,
        latency_ms=137,
    )

    assert event == {
        "event": "backend_request",
        "request_id": "req_abcdef1234567890abcdef1234567890",
        "method": "POST",
        "path": "/api/match",
        "status_code": 200,
        "status_category": "success",
        "latency_bucket": "100_249ms",
        "error_category": "",
        "raw_body_logged": False,
        "raw_message_logged": False,
        "provider_response_logged": False,
        "secrets_logged": False,
    }


def test_safe_request_log_event_sanitizes_unknown_path() -> None:
    event = build_safe_request_log_event(
        request_id="closed-beta-smoke-001",
        method="get",
        path="/api/match/raw-private-message-secret-111",
        status_code=404,
        latency_ms=18,
    )

    assert event["path"] == "unmatched_route"
    assert "raw-private-message-secret-111" not in str(event)


def test_request_id_normalization_rejects_secret_like_safe_prefixes() -> None:
    for unsafe_request_id in (
        "req_secret_token_1234",
        "trace_abcdef12_secret",
        "closed-beta-smoke-secret-token",
        "smoke_private_message",
        "sk-test-123",
        "abcdef1234567890abcdef1234567890",
        "550e8400-e29b-41d4-a716-446655440000",
    ):
        normalized = normalize_request_id(unsafe_request_id)
        assert normalized != unsafe_request_id
        assert normalized.startswith("req_")
        assert "secret" not in normalized
        assert "token" not in normalized
        assert "private" not in normalized


def test_match_request_logging_omits_raw_message_content(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))
    private_message = "third party private message with secret-token-123"

    response = client.post(
        "/api/match",
        json={
            "conversation_id": "synthetic_logging_check",
            "messages": [
                {
                    "id": "m1",
                    "author": "self",
                    "text": "Can you confirm Friday at 3pm?",
                },
                {
                    "id": "m2",
                    "author": "other",
                    "text": private_message,
                },
            ],
        },
    )

    assert response.status_code == 200
    events = logged_safe_events(caplog)
    assert events
    assert events[-1]["path"] == "/api/match"
    assert events[-1]["raw_body_logged"] is False
    assert events[-1]["raw_message_logged"] is False
    assert private_message not in caplog.text
    assert "secret-token-123" not in caplog.text


def test_request_id_is_safe_and_query_string_is_not_logged(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))

    response = client.get(
        "/readyz?private=raw-message-secret",
        headers={"X-Request-ID": "unsafe request id with private-secret"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "unsafe request id with private-secret"
    events = logged_safe_events(caplog)
    assert events[-1]["path"] == "/readyz"
    assert "raw-message-secret" not in caplog.text
    assert "private-secret" not in caplog.text


def test_client_supplied_opaque_request_ids_are_not_echoed_or_logged(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))
    supplied_ids = (
        "abcdef1234567890abcdef1234567890",
        "550e8400-e29b-41d4-a716-446655440000",
        "req_abcdef1234567890abcdef1234567890",
    )

    for supplied_id in supplied_ids:
        response = client.get("/readyz", headers={"X-Request-ID": supplied_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] != supplied_id
        assert response.headers["X-Request-ID"].startswith("req_")
        assert supplied_id not in caplog.text


def test_auth_cookie_and_query_values_are_not_logged(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))
    raw_secret = "raw-header-cookie-query-secret-222"

    response = client.get(
        f"/legal/privacy?token={raw_secret}",
        headers={
            "Authorization": f"Bearer {raw_secret}",
            "Cookie": f"session={raw_secret}",
        },
    )

    assert response.status_code == 200
    assert raw_secret not in caplog.text


def test_raw_text_in_unknown_url_path_is_not_logged(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))

    response = client.get("/legal/raw-private-message-secret-000")

    assert response.status_code == 404
    events = logged_safe_events(caplog)
    assert events[-1]["path"] == "/legal/{page}"
    assert "raw-private-message-secret-000" not in caplog.text


def test_secret_like_request_id_is_not_echoed_or_logged(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))

    response = client.get("/readyz", headers={"X-Request-ID": "req_secret_token_1234"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "req_secret_token_1234"
    assert "req_secret_token_1234" not in caplog.text


def test_unhandled_exceptions_return_generic_error_and_safe_log(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    app = create_app(BackendSettings())

    @app.get("/test/unhandled")
    def unhandled() -> None:
        raise RuntimeError("raw private chat should not be exposed")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/test/unhandled", headers={"X-Request-ID": "req_deadbeef"})

    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "Internal server error."
    assert body["request_id"].startswith("req_")
    assert body["request_id"] != "req_deadbeef"
    events = logged_safe_events(caplog)
    assert events[-1]["status_code"] == 500
    assert events[-1]["status_category"] == "server_error"
    assert events[-1]["error_category"] == "unhandled_exception"
    assert "raw private chat" not in response.text
    assert "raw private chat" not in caplog.text


def test_framework_validation_errors_do_not_echo_raw_payload_input(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))
    raw_secret = "raw-private-message-secret-422"

    probes = (
        {"json": raw_secret},
        {"json": [raw_secret]},
        {"json": 123},
        {
            "content": '{"messages": "raw-private-message-secret-malformed"',
            "headers": {"Content-Type": "application/json"},
        },
    )

    for probe in probes:
        response = client.post("/api/match", **probe)

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid request payload."}
        assert raw_secret not in response.text
        assert "raw-private-message-secret-malformed" not in response.text

    assert raw_secret not in caplog.text
    assert "raw-private-message-secret-malformed" not in caplog.text


def test_match_runtime_exception_does_not_expose_raw_exception_text(monkeypatch, caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    def fail_match(_payload):
        raise RuntimeError("raw private chat secret-456")

    monkeypatch.setattr(match_route, "match_conversation", fail_match)
    client = TestClient(create_app(BackendSettings()))

    response = client.post(
        "/api/match",
        json={
            "conversation_id": "synthetic_runtime_failure",
            "messages": [{"id": "m1", "author": "self", "text": "hello"}],
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "match service unavailable"
    assert "raw private chat" not in response.text
    assert "secret-456" not in response.text
    assert "raw private chat" not in caplog.text
    assert "secret-456" not in caplog.text


def test_match_value_error_does_not_expose_raw_exception_text(monkeypatch, caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    def fail_match(_payload):
        raise ValueError("raw private chat secret-789")

    monkeypatch.setattr(match_route, "match_conversation", fail_match)
    client = TestClient(create_app(BackendSettings()))

    response = client.post(
        "/api/match",
        json={
            "conversation_id": "synthetic_value_failure",
            "messages": [{"id": "m1", "author": "self", "text": "hello"}],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "match request could not be processed safely"
    assert "raw private chat" not in response.text
    assert "secret-789" not in response.text
    assert "raw private chat" not in caplog.text
    assert "secret-789" not in caplog.text


def test_analyze_validation_error_omits_unique_raw_text(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))
    raw_secret = "hidden intent raw-analyze-secret-654"

    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "synthetic_analyze_validation",
            "messages": [{"id": "m1", "author": "self", "text": raw_secret}],
        },
    )

    assert response.status_code == 400
    assert "raw-analyze-secret-654" not in response.text
    assert "raw-analyze-secret-654" not in caplog.text


def test_event_route_stores_bounded_metadata_only(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))
    raw_secret = "raw third-party private event secret-999"

    response = client.post(
        "/api/events/analysis",
        json={
            "event_id": raw_secret,
            "client_timestamp": raw_secret,
            "text": raw_secret,
            "message": raw_secret,
            "raw_body": raw_secret,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["raw_payload_persisted"] is False
    assert body["stored_event"]["event_id"] != raw_secret
    assert body["stored_event"]["client_timestamp"] == ""
    assert raw_secret not in response.text
    assert raw_secret not in str(EVENT_ROWS[-1])
    assert raw_secret not in caplog.text

    safe_response = client.post(
        "/api/events/state",
        json={"event_id": "evt_safe_123", "client_timestamp": 1712652000000},
    )

    assert safe_response.status_code == 200
    assert safe_response.json()["stored_event"]["event_id"] == "evt_safe_123"
    assert safe_response.json()["stored_event"]["client_timestamp"] == "1712652000000"


def test_feedback_route_does_not_return_store_or_log_raw_comment(caplog) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)
    client = TestClient(create_app(BackendSettings()))
    raw_comment = "raw feedback private message secret-321"

    response = client.post(
        "/api/feedback",
        json={
            "match_id": "vibe_match_safe_logging",
            "rating": 1,
            "comment": raw_comment,
            "consent_to_store_feedback": True,
        },
    )

    assert response.status_code == 200
    assert raw_comment not in response.text
    assert raw_comment not in str(FEEDBACK_ROWS[-1])
    assert raw_comment not in caplog.text
