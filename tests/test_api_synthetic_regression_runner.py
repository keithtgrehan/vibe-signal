from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from tools import generate_synthetic_whatsapp_fixtures as runner
from tools import run_synthetic_fixture_regression as regression_runner


class FakeResponse:
    status = 200
    headers = {}

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self, _limit: int) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_api_mode_calls_analyze_and_writes_separate_response_results(monkeypatch, tmp_path: Path) -> None:
    seen_payloads: list[dict] = []

    def fake_urlopen(request, timeout):  # noqa: ANN001
        assert timeout == 15.0
        assert urlparse(request.full_url).path == "/api/analyze"
        payload = json.loads(request.data.decode("utf-8"))
        seen_payloads.append(payload)
        return FakeResponse(
            {
                "conversation_id": payload["conversation_id"],
                "analysis_mode": "deterministic_local_only",
                "signal_state": "ready",
                "signal_strength": "low",
                "low_signal_fallback": False,
                "provider_used": False,
                "raw_chat_persisted": False,
                "safe_summary": "Cue evidence only; no fit, motive, deception, or emotional-state estimate.",
                "cannot_infer": ["private feelings or motives"],
                "evidence": [
                    {
                        "cue_id": "directness",
                        "cue_family": "directness",
                        "evidence_text": "Can you",
                        "span_start": 0,
                        "span_end": 7,
                        "safe_phrase": "message contains direct request wording.",
                        "explanation": "Rule matched direct request wording.",
                    }
                ],
            }
        )

    monkeypatch.setattr(runner, "urlopen", fake_urlopen)
    out_dir = tmp_path / "fixtures"
    report_dir = tmp_path / "engine_eval"

    exit_code = runner.main(
        [
            "--messages",
            "22",
            "--api-url",
            "http://localhost:5000",
            "--limit",
            "5",
            "--out-dir",
            str(out_dir),
            "--engine-report-dir",
            str(report_dir),
        ]
    )

    assert exit_code == 0
    assert len(seen_payloads) == 5
    assert all(payload["synthetic"] is True for payload in seen_payloads)
    assert all(payload["not_copied_from_real_chat"] is True for payload in seen_payloads)
    assert (out_dir / "conversations.jsonl").exists()
    assert not (out_dir / "evaluations.jsonl").exists()
    responses = _read_jsonl(report_dir / "api_responses.jsonl")
    results = _read_jsonl(report_dir / "api_regression_results.jsonl")
    assert len(responses) == 5
    assert len(results) == 5
    assert "API regression pass rate" in (report_dir / "api_regression_report.md").read_text(encoding="utf-8")


def test_api_url_validation_rejects_paths_and_credentials() -> None:
    for value in ("https://user:pass@example.test", "https://example.test/api", "ftp://example.test"):
        try:
            runner.normalize_api_url(value)
        except ValueError:
            pass
        else:
            raise AssertionError(value)


def test_synthetic_fixture_regression_runner_reads_existing_fixtures(monkeypatch, tmp_path: Path) -> None:
    conversations = runner.build_conversations(22)
    input_path = tmp_path / "conversations.jsonl"
    runner.write_jsonl(input_path, conversations)

    def fake_urlopen(request, timeout):  # noqa: ANN001
        assert timeout == 10.0
        assert urlparse(request.full_url).path == "/api/analyze"
        payload = json.loads(request.data.decode("utf-8"))
        expected = next(row for row in conversations if row["fixture_id"] == payload["conversation_id"])
        evidence = [
            {
                "cue_id": cue,
                "cue_family": cue,
                "evidence_text": expected["messages"][0]["text"],
                "span_start": 0,
                "span_end": len(expected["messages"][0]["text"]),
                "safe_phrase": "observable synthetic cue.",
                "explanation": "Synthetic regression test response.",
            }
            for cue in expected["expected_cues"]
        ]
        return FakeResponse(
            {
                "conversation_id": payload["conversation_id"],
                "analysis_mode": "deterministic_local_only",
                "signal_state": "low_signal" if expected["expected_result_type"] == "low_signal" else "ready",
                "signal_strength": "insufficient" if expected["expected_result_type"] == "low_signal" else "low",
                "low_signal_fallback": expected["expected_result_type"] == "low_signal",
                "provider_used": False,
                "raw_chat_persisted": False,
                "safe_summary": "Cue evidence only; no fit, motive, deception, or emotional-state estimate.",
                "cannot_infer": ["private feelings or motives"],
                "evidence": evidence,
            }
        )

    monkeypatch.setattr(runner, "urlopen", fake_urlopen)
    report_dir = tmp_path / "engine_eval"

    exit_code = regression_runner.main(
        [
            "--input",
            str(input_path),
            "--api-url",
            "http://localhost:5000",
            "--limit",
            "5",
            "--engine-report-dir",
            str(report_dir),
        ]
    )

    assert exit_code == 0
    assert len(_read_jsonl(report_dir / "synthetic_regression_api_responses.jsonl")) == 5
    assert len(_read_jsonl(report_dir / "synthetic_regression_results.jsonl")) == 5
    assert "Synthetic Fixture API Regression Report" in (report_dir / "synthetic_regression_report.md").read_text(encoding="utf-8")
