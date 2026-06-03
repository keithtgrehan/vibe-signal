from __future__ import annotations

from scripts import closed_beta_gate_check as gate


def test_closed_beta_gate_blocks_without_manual_human_gates(monkeypatch) -> None:
    monkeypatch.setattr(gate, "_run", lambda command: {"command": " ".join(command), "status": "PASS", "returncode": 0, "output": ""})
    monkeypatch.setattr(gate, "_exists", lambda path: True)

    summary = gate.build_gate_summary(deploy_status="current")

    assert summary["tester_invite_decision"] == "BLOCKED"
    assert summary["gates"]["human_reviewed_labels"]["status"] == "MANUAL_REQUIRED"
    assert summary["gates"]["legal_privacy_review"]["status"] == "MANUAL_REQUIRED"
    assert summary["gates"]["real_device_qa"]["status"] == "MANUAL_REQUIRED"


def test_closed_beta_gate_marks_deploy_unverified_as_manual_required(monkeypatch) -> None:
    monkeypatch.setattr(gate, "_run", lambda command: {"command": " ".join(command), "status": "PASS", "returncode": 0, "output": ""})
    monkeypatch.setattr(gate, "_exists", lambda path: True)

    summary = gate.build_gate_summary(deploy_status="unverified")

    assert summary["gates"]["deployed_backend_version"]["status"] == "MANUAL_REQUIRED"
    assert summary["tester_invite_decision"] == "BLOCKED"
