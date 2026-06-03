from __future__ import annotations

from pathlib import Path

from scripts.check_no_raw_content_leaks import build_summary, scan_paths


def test_no_raw_content_leak_scan_passes_repo_surfaces() -> None:
    summary = build_summary(scan_paths())

    assert summary["status"] == "pass"
    assert summary["finding_count"] == 0


def test_no_raw_content_leak_scan_blocks_feedback_hash(tmp_path: Path) -> None:
    probe = tmp_path / "storage.py"
    probe.write_text('row = {"comment_sha256": hash_comment(comment)}\n', encoding="utf-8")

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "fail"
    assert summary["findings"][0]["pattern_id"] == "feedback_comment_hash"
