from dataclasses import dataclass

from src.app.agents.base import load_prompt


@dataclass
class RequirementsAgentConfig:
    prompt_file: str = "requirements.md"


def get_requirements_prompt() -> str:
    return load_prompt(RequirementsAgentConfig.prompt_file)
