from pathlib import Path
from typing import Iterable


PROMPT_DIR = Path(__file__).resolve().parents[3] / "prompts"
REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


def load_prompt(filename: str) -> str:
    return (PROMPT_DIR / filename).read_text(encoding="utf-8")


def collapse_confidence(levels: Iterable[str]) -> str:
    filtered = [level for level in levels if level in CONFIDENCE_ORDER]
    if not filtered:
        return "low"
    return min(filtered, key=lambda level: CONFIDENCE_ORDER[level])


def dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if not item:
            continue
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def module_area(locator: str) -> str:
    path = locator.lower()
    if "api/" in path:
        return "api layer"
    if "service" in path:
        return "service layer"
    if "contract" in path or "schema" in path:
        return "schema layer"
    if "tool" in path:
        return "tool layer"
    if "storage" in path or "repository" in path:
        return "storage layer"
    if "doc" in path or path.endswith(".md"):
        return "documentation"
    if "test" in path:
        return "test suite"
    return locator
