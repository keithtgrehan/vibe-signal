from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = ("docs", "configs", "scripts", "src", "tests")
PORTED_PREFIXES = (
    Path("configs"),
    Path("docs/control_room"),
    Path("docs/evaluation"),
    Path("docs/research"),
    Path("schemas"),
    Path("scripts"),
    Path("src/vibesignal_ai/evidence"),
    Path("src/vibesignal_ai/features/cue_taxonomy.py"),
    Path("src/vibesignal_ai/features/neuro_support.py"),
    Path("src/vibesignal_ai/safety/redline_output_blocker.py"),
    Path("src/vibesignal_ai/safety/redline_policy.json"),
    Path("src/vibesignal_ai/safety/blocked_phrases.yml"),
    Path("tests/fixtures"),
)
ALLOWED_RESIDUE_FILES = {
    Path("docs/control_room/agent_r5_signal_engine_to_vibe_port_map.md"),
    Path("tests/test_no_source_domain_residue.py"),
}
FORBIDDEN_SOURCE_TERMS = (
    r"\bticker\b",
    r"\btrading\b",
    r"\balpha\b",
    r"\bbuy signal\b",
    r"\bsell signal\b",
    r"\bearnings call\b",
    r"\brevenue guidance\b",
    r"\beps\b",
    r"\banalyst pressure\b",
    r"\bmarket signal\b",
    r"\binvestor relations\b",
    r"\bsec edgar\b",
)
FORBIDDEN_TRAINING_IMPLEMENTATION_TERMS = (
    "TfidfVectorizer",
    "LogisticRegression",
    ".fit(",
    "sklearn",
    "torch",
    "transformers",
    "datasets",
    "sentence_transformers",
    "faiss",
    "chromadb",
    "mlflow",
)


def iter_repo_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts:
                continue
            relative = path.relative_to(ROOT)
            if any(relative == prefix or str(relative).startswith(str(prefix) + "/") for prefix in PORTED_PREFIXES):
                files.append(path)
    return files


def rel(path: Path) -> Path:
    return path.relative_to(ROOT)


def test_no_forbidden_source_domain_residue_outside_r5_map() -> None:
    hits: list[str] = []
    for path in iter_repo_files():
        relative = rel(path)
        if relative in ALLOWED_RESIDUE_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for pattern in FORBIDDEN_SOURCE_TERMS:
            if re.search(pattern, text):
                hits.append(f"{relative}: {pattern}")

    assert hits == []


def test_no_training_implementation_added_to_code() -> None:
    hits: list[str] = []
    for path in iter_repo_files():
        relative = rel(path)
        if not (str(relative).startswith("scripts/") or str(relative).startswith("src/")):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term in FORBIDDEN_TRAINING_IMPLEMENTATION_TERMS:
            if term in text:
                hits.append(f"{relative}: {term}")

    assert hits == []
