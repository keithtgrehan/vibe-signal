#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_NEUTRAL_SOURCE_IDS = {
    "private_whatsapp_source_001",
    "consented_private_source_001",
}
TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".jsonl",
    ".jsx",
    ".md",
    ".py",
    ".sh",
    ".svg",
    ".toml",
    ".txt",
    ".ts",
    ".tsx",
    ".yml",
    ".yaml",
}


def _name_token(*codes: int) -> str:
    return "".join(chr(code) for code in codes)


_NAME_A = _name_token(108, 97, 117, 114, 97)
_NAME_B = _name_token(98, 105, 98, 105)
_PRIOR_SOURCE_ID = f"private_whatsapp_{_NAME_A}_{_NAME_B}"
_PRIVATE_ROOT_PARTS = ("data", "restricted", "private_whatsapp")
_PRIVATE_ROOT = "/".join(_PRIVATE_ROOT_PARTS)
_PRIVATE_AREAS = ("raw", "processed", "models", "reports")
_PRIVATE_FILE_NAMES = (
    "private_label_review_100" + ".csv",
    "private_label_review_100" + ".xlsx",
    "private_messages" + ".jsonl",
    "private_messages_redacted" + ".jsonl",
    "private_dynamics_baseline" + ".pkl",
    "weak_label_baseline" + ".pkl",
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    category: str


def _run_git_ls_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        text=False,
        capture_output=True,
        check=True,
    )
    paths = result.stdout.decode("utf-8", errors="replace").split("\0")
    return [REPO_ROOT / path for path in paths if path]


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _is_text_file(path: Path) -> bool:
    if path.name in {"README", ".gitignore"}:
        return True
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.parent.name == "workflows" and path.suffix.lower() in {".yml", ".yaml"}


def _expand_supplied_paths(raw_paths: list[str]) -> list[Path]:
    selected: list[Path] = []
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.is_dir():
            selected.extend(item for item in path.rglob("*") if item.is_file())
        elif path.is_file():
            selected.append(path)
        else:
            selected.append(path)
    return sorted(set(selected))


def _web_dist_paths() -> list[Path]:
    dist = REPO_ROOT / "web" / "dist"
    if not dist.exists():
        return []
    return [path for path in dist.rglob("*") if path.is_file()]


def _selected_paths(args: argparse.Namespace) -> list[Path]:
    if args.paths:
        selected = _expand_supplied_paths(args.paths)
    else:
        selected = _run_git_ls_files()
    if args.include_web_dist:
        selected.extend(_web_dist_paths())
    return sorted(set(selected))


def _line_patterns() -> list[tuple[str, re.Pattern[str]]]:
    private_artifact_path = re.compile(
        re.escape(_PRIVATE_ROOT) + r"/(?:" + "|".join(re.escape(area) for area in _PRIVATE_AREAS) + r")/",
        flags=re.IGNORECASE,
    )
    private_filenames = re.compile("|".join(re.escape(name) for name in _PRIVATE_FILE_NAMES), flags=re.IGNORECASE)
    raw_export_filename = re.compile(r"\b(?:private[_-]?)?whatsapp[^/\n\r]*(?:export|chat)[^/\n\r]*\.zip\b", flags=re.IGNORECASE)
    real_person_source = re.compile(re.escape(_PRIOR_SOURCE_ID), flags=re.IGNORECASE)
    real_name_token = re.compile(r"\b(?:" + re.escape(_NAME_A) + r"|" + re.escape(_NAME_B) + r")\b", flags=re.IGNORECASE)
    return [
        ("private_artifact_path", private_artifact_path),
        ("private_artifact_filename", private_filenames),
        ("private_whatsapp_export_filename", raw_export_filename),
        ("real_person_private_source_identifier", real_person_source),
        ("real_person_private_metadata_token", real_name_token),
    ]


def _path_patterns() -> list[tuple[str, re.Pattern[str]]]:
    return [
        (
            "private_artifact_path",
            re.compile(
                re.escape(_PRIVATE_ROOT) + r"/(?:" + "|".join(re.escape(area) for area in _PRIVATE_AREAS) + r")/",
                flags=re.IGNORECASE,
            ),
        ),
        ("real_person_private_source_identifier", re.compile(re.escape(_PRIOR_SOURCE_ID), flags=re.IGNORECASE)),
    ]


def _is_allowed(path: Path, category: str, line: str) -> bool:
    rel = _display_path(path)
    if category == "private_artifact_filename" and rel.startswith("tools/"):
        return True
    if category == "private_artifact_filename" and rel == "tests/test_private_data_hygiene.py":
        return True
    if category == "private_artifact_path" and line.strip() == f"- keep private data under `{_PRIVATE_ROOT}/**`":
        return True
    if category == "private_artifact_path" and f"{_PRIVATE_ROOT}/**" in line and not any(f"{_PRIVATE_ROOT}/{area}/" in line for area in _PRIVATE_AREAS):
        return True
    return False


def _scan_private_source_config_keys(path: Path, text: str) -> list[Finding]:
    rel = _display_path(path)
    if not rel.startswith("configs/"):
        return []
    if "private" not in path.name and "training" not in path.name:
        return []

    findings: list[Finding] = []
    key_re = re.compile(r"^(?P<key>[A-Za-z0-9_-]+):\s*(?:#.*)?$")
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = key_re.match(line)
        if not match:
            continue
        key = match.group("key")
        if ("private" in key or "whatsapp" in key) and key not in ALLOWED_NEUTRAL_SOURCE_IDS:
            findings.append(Finding(rel, line_number, "non_neutral_private_source_id"))
    return findings


def _scan_path(path: Path) -> list[Finding]:
    rel = _display_path(path)
    findings: list[Finding] = []
    for category, pattern in _path_patterns():
        if pattern.search(rel):
            findings.append(Finding(rel, 0, category))

    if not path.exists() or not path.is_file() or not _is_text_file(path):
        return findings

    text = path.read_text(encoding="utf-8", errors="replace")
    findings.extend(_scan_private_source_config_keys(path, text))
    for line_number, line in enumerate(text.splitlines(), start=1):
        for category, pattern in _line_patterns():
            if pattern.search(line) and not _is_allowed(path, category, line):
                findings.append(Finding(rel, line_number, category))
    return findings


def scan(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        findings.extend(_scan_path(path))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check tracked/public surfaces for private WhatsApp metadata exposure.")
    parser.add_argument("paths", nargs="*", help="Optional files/directories to scan. Defaults to tracked git files only.")
    parser.add_argument("--include-web-dist", action="store_true", help="Also scan web/dist when it exists.")
    args = parser.parse_args(argv)

    findings = scan(_selected_paths(args))
    if findings:
        sys.stdout.write(f"Private metadata exposure check failed: {len(findings)} finding(s).\n")
        for finding in findings:
            line = f":{finding.line}" if finding.line else ""
            sys.stdout.write(f"- {finding.path}{line} {finding.category}\n")
        return 1

    sys.stdout.write("Private metadata exposure check passed: 0 finding(s).\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
