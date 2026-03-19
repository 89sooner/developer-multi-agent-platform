from dataclasses import dataclass

from src.app.agents.base import load_prompt


@dataclass
class ImplementationAgentConfig:
    prompt_file: str = "implementation.md"


def get_implementation_prompt() -> str:
    return load_prompt(ImplementationAgentConfig.prompt_file)
