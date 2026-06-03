from __future__ import annotations

from pathlib import Path

from scripts.check_public_copy_safety import build_summary, scan_paths


def test_public_copy_safety_scan_passes_configured_surfaces() -> None:
    summary = build_summary(scan_paths())

    assert summary["status"] == "pass"
    assert summary["unallowed_count"] == 0


def test_public_copy_safety_scan_blocks_unallowlisted_claim(tmp_path: Path) -> None:
    probe = tmp_path / "public.md"
    probe.write_text("Find out what they really think with guaranteed results.\n", encoding="utf-8")

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "fail"
    assert {finding["pattern_id"] for finding in summary["findings"]} >= {"find_out_think", "guaranteed"}
