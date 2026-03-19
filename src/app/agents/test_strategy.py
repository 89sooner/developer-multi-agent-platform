from dataclasses import dataclass

from src.app.agents.base import load_prompt


@dataclass
class TestStrategyAgentConfig:
    prompt_file: str = "test_strategy.md"


def get_test_strategy_prompt() -> str:
    return load_prompt(TestStrategyAgentConfig.prompt_file)
