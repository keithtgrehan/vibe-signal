from __future__ import annotations

import json
from urllib.parse import urlparse

from scripts import smoke_test_production_analyze as smoke


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
    if path == "/healthz":
        assert method == "GET"
        return smoke.TransportResponse(
            200,
            {"x-request-id": REQUEST_ID},
            json.dumps({"status": "ok", "service": "vibe-signal-backend"}),
        )
    if path == "/api/status":
        assert method == "GET"
        return smoke.TransportResponse(
            200,
            {"x-request-id": REQUEST_ID},
            json.dumps(
                {
                    "ok": True,
                    "service": "vibe-signal-backend",
                    "raw_message_persistence_enabled": False,
                    "raw_message_logging_enabled": False,
                    "analytics_tracking_enabled": False,
                    "training_enabled": False,
                    "git_commit": "abc123",
                    "deploy_version": "unknown",
                    "build_timestamp": "unknown",
                    "service_revision": "vibe-signal",
                }
            ),
        )
    if path == "/api/analyze":
        assert method == "POST"
        assert headers["Content-Type"] == "application/json"
        assert body is not None
        assert json.loads(body.decode("utf-8")) == smoke.SYNTHETIC_ANALYZE_PAYLOAD
        return smoke.TransportResponse(
            200,
            {"x-request-id": REQUEST_ID},
            json.dumps(
                {
                    "conversation_id": "synthetic_production_analyze_smoke",
                    "analysis_mode": "deterministic_local_only",
                    "provider_used": False,
                    "raw_chat_persisted": False,
                    "safe_summary": "Cue evidence only.",
                    "cannot_infer": ["private feelings or motives"],
                    "evidence": [
                        {
                            "evidence_id": "ev_1",
                            "safe_phrase": "message contains hedging wording.",
                            "explanation": "Rule matched tentative wording.",
                        }
                    ],
                }
            ),
        )
    return smoke.TransportResponse(404, {"x-request-id": REQUEST_ID}, "")


def test_production_analyze_smoke_endpoint_list_is_minimal() -> None:
    assert smoke.SMOKE_ENDPOINTS == ("/healthz", "/api/status", "/api/analyze")


def test_production_analyze_smoke_payload_uses_only_safe_synthetic_text() -> None:
    assert smoke.SYNTHETIC_ANALYZE_PAYLOAD == {
        "conversation_id": "synthetic_production_analyze_smoke",
        "text": "self: Are we still on for Friday?\nother: maybe later, not sure yet",
    }

    serialized = json.dumps(smoke.SYNTHETIC_ANALYZE_PAYLOAD).lower()
    for blocked in ("password", "api_key", "bearer", "private chat", "medical", "financial"):
        assert blocked not in serialized


def test_run_smoke_checks_passes_with_safe_fake_transport() -> None:
    results = smoke.run_smoke_checks("https://api.example.test", transport=fake_success_transport)

    assert [result.path for result in results] == list(smoke.SMOKE_ENDPOINTS)
    assert all(result.ok for result in results)
    assert all(result.request_id == REQUEST_ID for result in results)


def test_analyze_validation_blocks_unsafe_user_facing_claims() -> None:
    payload = {
        "conversation_id": "synthetic_production_analyze_smoke",
        "analysis_mode": "deterministic_local_only",
        "provider_used": False,
        "raw_chat_persisted": False,
        "safe_summary": "This proves they like you.",
        "cannot_infer": [],
        "evidence": [],
    }

    assert smoke.validate_analyze(payload) == "analyze_unsafe_user_facing_claim"


def test_main_prints_metadata_only_without_synthetic_text(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        smoke,
        "run_smoke_checks",
        lambda *_args, **_kwargs: [
            smoke.SmokeResult("GET", "/healthz", True, 200, "ok", REQUEST_ID),
            smoke.SmokeResult("GET", "/api/status", True, 200, "ok", REQUEST_ID),
            smoke.SmokeResult("POST", "/api/analyze", True, 200, "ok", REQUEST_ID),
        ],
    )

    exit_code = smoke.main(["--base-url", "https://api.example.test"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Summary: 3/3 production analyze smoke checks passed." in captured.out
    assert "Are we still on for Friday" not in captured.out
