from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parents[3] / "prompts"


def load_prompt(filename: str) -> str:
    return (PROMPT_DIR / filename).read_text(encoding="utf-8")
