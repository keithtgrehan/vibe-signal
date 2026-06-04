#!/usr/bin/env python3
"""Validate Vibe Signal agent prompt docs."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "docs" / "agents"

REQUIRED_AGENT_FILES = (
    "controller_agent.md",
    "agent_1_product_psychology_ethics.md",
    "agent_2_dataset_rights_gate.md",
    "agent_3_nlp_engine_eval.md",
    "agent_4_trust_explainability_safe_output_ux.md",
    "agent_5_ios_testflight_launch.md",
    "agent_6_web_growth_landing_page.md",
    "agent_7_competitive_category_research.md",
    "agent_8_codex_implementation_planner.md",
    "deployment_production_agent.md",
    "safety_copy_guardrail_agent.md",
    "recruiter_demo_agent.md",
    "human_labeling_agent.md",
    "closed_beta_gate_agent.md",
    "ui_ux_product_design_agent.md",
    "repo_maintenance_agent.md",
)

REQUIRED_SECTIONS = (
    "Agent Name",
    "Goal",
    "Purpose",
    "When To Run",
    "Inputs",
    "Branch Naming Convention",
    "Tasks",
    "Hard Boundaries",
    "Files Usually Touched",
    "Files Not To Touch",
    "Validation Commands",
    "Expected Outputs",
    "Final Output",
    "PR Body Checklist",
    "Failure Conditions",
    "Example Prompt",
)

REQUIRED_BOUNDARIES = (
    "no raw private chats",
    "no unsafe relationship claims",
    "no legal/compliance overclaim",
    "no model-accuracy overclaim",
    "synthetic examples only",
    "human gates remain human",
)

UNSAFE_PRODUCT_CLAIMS = (
    r"\bcan detect cheating\b",
    r"\bcheating detector\b",
    r"\bpredicts? attraction\b",
    r"\bdetects? hidden intent\b",
    r"\bdetects? lies?\b",
    r"\bdiagnoses?\b",
    r"\bvalidated accuracy\b",
    r"\bproduction-grade\b",
    r"\bguaranteed\b",
)


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lower = text.lower()

    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in text:
            errors.append(f"{path}: missing section ## {section}")

    for boundary in REQUIRED_BOUNDARIES:
        if boundary not in lower:
            errors.append(f"{path}: missing hard boundary phrase {boundary!r}")

    for pattern in UNSAFE_PRODUCT_CLAIMS:
        if re.search(pattern, lower):
            errors.append(f"{path}: unsafe product claim matched {pattern!r}")

    return errors


def main() -> int:
    errors: list[str] = []

    if not AGENT_DIR.is_dir():
        print("docs/agents directory is missing", file=sys.stderr)
        return 1

    for filename in REQUIRED_AGENT_FILES:
        path = AGENT_DIR / filename
        if not path.is_file():
            errors.append(f"missing agent doc: {path}")
            continue
        errors.extend(validate_file(path))

    for guide in (
        "README.md",
        "agentic_workflow_guide.md",
        "merge_order_playbook.md",
        "parallel_worktree_strategy.md",
        "manual_human_gates.md",
        "sprint_templates.md",
    ):
        if not (AGENT_DIR / guide).is_file():
            errors.append(f"missing agent guide: {AGENT_DIR / guide}")

    if errors:
        for error in errors:
            print(f"[FAIL] {error}", file=sys.stderr)
        return 1

    print(f"Agent control-room check passed: {len(REQUIRED_AGENT_FILES)} agent docs verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
