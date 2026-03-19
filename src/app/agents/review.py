from dataclasses import dataclass

from src.app.agents.base import load_prompt


@dataclass
class ReviewAgentConfig:
    prompt_file: str = "review.md"


def get_review_prompt() -> str:
    return load_prompt(ReviewAgentConfig.prompt_file)
