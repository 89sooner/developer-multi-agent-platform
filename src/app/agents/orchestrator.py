from dataclasses import dataclass

from src.app.agents.base import load_prompt


@dataclass
class OrchestratorConfig:
    prompt_file: str = "orchestrator.md"


def get_orchestrator_prompt() -> str:
    return load_prompt(OrchestratorConfig.prompt_file)
