from dataclasses import dataclass

from src.app.agents.base import load_prompt


@dataclass
class RepoContextAgentConfig:
    prompt_file: str = "repo_context.md"


def get_repo_context_prompt() -> str:
    return load_prompt(RepoContextAgentConfig.prompt_file)
