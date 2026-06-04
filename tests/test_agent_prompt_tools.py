from pathlib import Path

from scripts import agent_control_room_check
from scripts import print_agent_prompt


def test_print_agent_prompt_lists_controller() -> None:
    prompts = print_agent_prompt.available_agents()

    assert any(prompt.key == "controller" for prompt in prompts)
    assert any(prompt.path.name == "controller_agent.md" for prompt in prompts)


def test_print_agent_prompt_resolves_alias() -> None:
    path = print_agent_prompt.resolve_agent("engine_eval")

    assert path.name == "agent_3_nlp_engine_eval.md"
    assert "Agent 3 - NLP Engine Evaluation" in path.read_text(encoding="utf-8")


def test_agent_control_room_check_passes_current_docs() -> None:
    assert agent_control_room_check.main() == 0


def test_agent_docs_preserve_required_boundaries() -> None:
    docs = Path("docs/agents").glob("*.md")
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in docs)

    for phrase in (
        "no raw private chats",
        "no unsafe relationship claims",
        "no legal/compliance overclaim",
        "no model-accuracy overclaim",
        "synthetic examples only",
        "human gates remain human",
    ):
        assert phrase in combined
