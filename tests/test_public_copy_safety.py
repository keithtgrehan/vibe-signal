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


def test_public_copy_safety_allows_explicit_vibe_signal_limit_sentence(tmp_path: Path) -> None:
    probe = tmp_path / "public.md"
    probe.write_text(
        "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.\n",
        encoding="utf-8",
    )

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "pass"


def test_public_copy_safety_still_blocks_unallowlisted_attraction_claim(tmp_path: Path) -> None:
    probe = tmp_path / "public.md"
    probe.write_text("Vibe Signal can tell if they like you.\n", encoding="utf-8")

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "fail"
    assert {finding["pattern_id"] for finding in summary["findings"]} >= {"they_like_you"}


def test_public_copy_safety_still_blocks_hidden_intent_claim(tmp_path: Path) -> None:
    probe = tmp_path / "public.md"
    probe.write_text("This reveals hidden intent.\n", encoding="utf-8")

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "fail"
    assert {finding["pattern_id"] for finding in summary["findings"]} >= {"hidden_intent"}


def test_public_copy_safety_still_blocks_lying_claim(tmp_path: Path) -> None:
    probe = tmp_path / "public.md"
    probe.write_text("Vibe Signal can tell when they are lying.\n", encoding="utf-8")

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "fail"
    assert {finding["pattern_id"] for finding in summary["findings"]} >= {"lying_or_lies"}


def test_public_copy_safety_still_blocks_diagnosis_therapy_framing(tmp_path: Path) -> None:
    probe = tmp_path / "public.md"
    probe.write_text("Vibe Signal is therapy for their diagnosis.\n", encoding="utf-8")

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "fail"
    assert {finding["pattern_id"] for finding in summary["findings"]} >= {"diagnose"}


def test_public_copy_safety_still_blocks_make_them_respond_claim(tmp_path: Path) -> None:
    probe = tmp_path / "public.md"
    probe.write_text("Use this to make them respond.\n", encoding="utf-8")

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "fail"
    assert {finding["pattern_id"] for finding in summary["findings"]} >= {"make_them"}


def test_public_copy_safety_allows_exact_prohibited_use_sentence(tmp_path: Path) -> None:
    probe = tmp_path / "public.md"
    probe.write_text(
        "Prohibited use includes stalking, harassment, coercion, manipulation, or trying to make someone respond.\n",
        encoding="utf-8",
    )

    summary = build_summary(scan_paths([str(probe)]))

    assert summary["status"] == "pass"
