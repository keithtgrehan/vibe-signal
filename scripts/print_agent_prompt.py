#!/usr/bin/env python3
"""Print reusable Vibe Signal agent prompts from docs/agents."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "docs" / "agents"

ALIASES = {
    "controller": "controller_agent.md",
    "product_ethics": "agent_1_product_psychology_ethics.md",
    "dataset_rights": "agent_2_dataset_rights_gate.md",
    "engine_eval": "agent_3_nlp_engine_eval.md",
    "safe_output_ux": "agent_4_trust_explainability_safe_output_ux.md",
    "ios_testflight": "agent_5_ios_testflight_launch.md",
    "web_growth": "agent_6_web_growth_landing_page.md",
    "competitive_research": "agent_7_competitive_category_research.md",
    "implementation_planner": "agent_8_codex_implementation_planner.md",
    "deployment": "deployment_production_agent.md",
    "safety_copy": "safety_copy_guardrail_agent.md",
    "recruiter_demo": "recruiter_demo_agent.md",
    "human_labeling": "human_labeling_agent.md",
    "closed_beta_gate": "closed_beta_gate_agent.md",
    "ui_ux": "ui_ux_product_design_agent.md",
    "repo_maintenance": "repo_maintenance_agent.md",
}


@dataclass(frozen=True)
class AgentPrompt:
    key: str
    path: Path
    title: str


def agent_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("_", " ").title()


def available_agents() -> list[AgentPrompt]:
    prompts: list[AgentPrompt] = []
    for key, filename in sorted(ALIASES.items()):
        path = AGENT_DIR / filename
        if path.is_file():
            prompts.append(AgentPrompt(key, path, agent_title(path)))
    return prompts


def resolve_agent(name: str) -> Path:
    normalized = re.sub(r"[^a-z0-9_]+", "_", name.strip().lower()).strip("_")
    filename = ALIASES.get(normalized)
    if filename:
        path = AGENT_DIR / filename
        if path.is_file():
            return path

    direct = AGENT_DIR / name
    if direct.suffix != ".md":
        direct = AGENT_DIR / f"{normalized}.md"
    if direct.is_file():
        return direct

    available = ", ".join(prompt.key for prompt in available_agents())
    raise SystemExit(f"Unknown agent {name!r}. Available agents: {available}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print a Vibe Signal agent prompt.")
    parser.add_argument("agent", nargs="?", help="Agent key or markdown filename.")
    parser.add_argument("--list", action="store_true", help="List available agent prompt keys.")
    args = parser.parse_args(argv)

    if args.list:
        for prompt in available_agents():
            rel = prompt.path.relative_to(ROOT)
            print(f"{prompt.key}\t{prompt.title}\t{rel}")
        return 0

    if not args.agent:
        parser.error("provide an agent key or use --list")

    path = resolve_agent(args.agent)
    sys.stdout.write(path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
