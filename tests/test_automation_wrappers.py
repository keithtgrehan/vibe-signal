from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _fake_python(tmp_path: Path, *, deploy_status: str = "current", verify_exit: int = 0) -> Path:
    fake = tmp_path / "fake_python.py"
    fake.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            from __future__ import annotations

            import json
            import os
            import sys
            from pathlib import Path

            log_path = Path(os.environ["FAKE_PYTHON_LOG"])
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(sys.argv[1:]) + "\\n")

            script = sys.argv[1] if len(sys.argv) > 1 else ""
            if script.endswith("verify_deployed_version.py"):
                print(json.dumps({{"version_status": "{deploy_status}"}}))
                raise SystemExit({verify_exit})

            if script.endswith("closed_beta_gate_check.py"):
                deploy_status = "missing"
                report_out = ""
                for index, arg in enumerate(sys.argv):
                    if arg == "--deploy-status" and index + 1 < len(sys.argv):
                        deploy_status = sys.argv[index + 1]
                    if arg == "--report-out" and index + 1 < len(sys.argv):
                        report_out = sys.argv[index + 1]
                if report_out:
                    path = Path(report_out)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(
                        f"Final tester invite decision: `BLOCKED`\\nDeploy: {{deploy_status}}\\n",
                        encoding="utf-8",
                    )
                print(f"gate deploy status: {{deploy_status}}")
                raise SystemExit(0)

            print(f"stubbed {{script}}")
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return fake


def _read_log(log_path: Path) -> list[list[str]]:
    return [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]


def _run(command: list[str], *, env: dict[str, str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    base_env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"CLOSED_BETA_GATE_REPORT_OUT", "DEPLOY_STATUS", "EXPECTED_GIT_COMMIT", "WRITE_REPORT"}
    }
    return subprocess.run(
        command,
        cwd=cwd,
        env={**base_env, **env},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_prod_smoke_passes_current_git_commit_inside_repo(tmp_path: Path) -> None:
    log_path = tmp_path / "fake-python.log"
    fake_python = _fake_python(tmp_path)
    expected_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()

    completed = _run(
        ["bash", "scripts/prod_smoke_all.sh", "https://example.invalid"],
        env={"PYTHON": str(fake_python), "FAKE_PYTHON_LOG": str(log_path)},
    )

    assert completed.returncode == 0, completed.stdout
    verify_call = _read_log(log_path)[0]
    assert verify_call[:2] == ["scripts/verify_deployed_version.py", "--base-url"]
    assert "--expected-git-commit" in verify_call
    assert verify_call[verify_call.index("--expected-git-commit") + 1] == expected_commit


def test_prod_smoke_warns_and_falls_back_outside_git_repo(tmp_path: Path) -> None:
    script_root = tmp_path / "repo"
    scripts_dir = script_root / "scripts"
    scripts_dir.mkdir(parents=True)
    for name in ("_automation_common.sh", "prod_smoke_all.sh"):
        shutil.copy2(REPO_ROOT / "scripts" / name, scripts_dir / name)
    (scripts_dir / "verify_deployed_version.py").write_text("", encoding="utf-8")
    (scripts_dir / "smoke_test_production_analyze.py").write_text("", encoding="utf-8")

    log_path = tmp_path / "fake-python.log"
    fake_python = _fake_python(tmp_path)

    completed = _run(
        ["bash", str(scripts_dir / "prod_smoke_all.sh"), "https://example.invalid"],
        cwd=script_root,
        env={"PYTHON": str(fake_python), "FAKE_PYTHON_LOG": str(log_path)},
    )

    assert completed.returncode == 0, completed.stdout
    assert "Expected git commit unavailable; deployed version proof may be unverified." in completed.stdout
    verify_call = _read_log(log_path)[0]
    assert "--expected-git-commit" not in verify_call


def test_closed_beta_gate_passes_stale_deploy_status_to_checker(tmp_path: Path) -> None:
    log_path = tmp_path / "fake-python.log"
    fake_python = _fake_python(tmp_path, deploy_status="stale", verify_exit=1)

    completed = _run(
        ["bash", "scripts/closed_beta_gate_all.sh"],
        env={"PYTHON": str(fake_python), "FAKE_PYTHON_LOG": str(log_path)},
    )

    assert completed.returncode == 0, completed.stdout
    gate_call = [call for call in _read_log(log_path) if call[0] == "scripts/closed_beta_gate_check.py"][0]
    assert gate_call[gate_call.index("--deploy-status") + 1] == "stale"


def test_closed_beta_gate_passes_unverified_deploy_status_to_checker(tmp_path: Path) -> None:
    log_path = tmp_path / "fake-python.log"
    fake_python = _fake_python(tmp_path, deploy_status="unverified", verify_exit=0)

    completed = _run(
        ["bash", "scripts/closed_beta_gate_all.sh"],
        env={"PYTHON": str(fake_python), "FAKE_PYTHON_LOG": str(log_path)},
    )

    assert completed.returncode == 0, completed.stdout
    gate_call = [call for call in _read_log(log_path) if call[0] == "scripts/closed_beta_gate_check.py"][0]
    assert gate_call[gate_call.index("--deploy-status") + 1] == "unverified"


def test_closed_beta_gate_default_report_does_not_touch_tracked_report(tmp_path: Path) -> None:
    tracked_report = REPO_ROOT / "docs" / "proof" / "closed_beta" / "closed_beta_gate_report.md"
    before = tracked_report.read_text(encoding="utf-8")
    log_path = tmp_path / "fake-python.log"
    fake_python = _fake_python(tmp_path, deploy_status="current")

    completed = _run(
        ["bash", "scripts/closed_beta_gate_all.sh"],
        env={"PYTHON": str(fake_python), "FAKE_PYTHON_LOG": str(log_path)},
    )

    assert completed.returncode == 0, completed.stdout
    assert tracked_report.read_text(encoding="utf-8") == before
    gate_call = [call for call in _read_log(log_path) if call[0] == "scripts/closed_beta_gate_check.py"][0]
    assert gate_call[gate_call.index("--deploy-status") + 1] == "current"
    report_out = gate_call[gate_call.index("--report-out") + 1]
    assert report_out == "reports/automation/latest/closed_beta_gate_report.md"
