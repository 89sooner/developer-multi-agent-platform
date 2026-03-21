from __future__ import annotations

import hashlib
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[3] / "skills"
PROMPTS_ROOT = Path(__file__).resolve().parents[3] / "prompts"
SKILL_FILES = {
    "workflow-orchestrator": ["SKILL.md", "agents/openai.yaml"],
    "requirements-planner": ["SKILL.md", "agents/openai.yaml"],
    "repo-context-finder": ["SKILL.md", "agents/openai.yaml"],
    "implementation-planner": ["SKILL.md", "agents/openai.yaml"],
    "test-strategy-generator": ["SKILL.md", "agents/openai.yaml"],
    "review-gate": ["SKILL.md", "agents/openai.yaml"],
    "summary-composer": [],
}
PROMPT_FILES = {
    "workflow-orchestrator": "orchestrator.md",
    "requirements-planner": "requirements.md",
    "repo-context-finder": "repo_context.md",
    "implementation-planner": "implementation.md",
    "test-strategy-generator": "test_strategy.md",
    "review-gate": "review.md",
    "summary-composer": None,
}


def resolve_skill_versions(selected_agents: list[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for agent_name in selected_agents:
        versions[agent_name] = _compute_skill_version(agent_name)
    return versions


def resolve_prompt_versions(selected_agents: list[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for agent_name in selected_agents:
        versions[agent_name] = _compute_prompt_version(agent_name)
    return versions


def _compute_skill_version(skill_name: str) -> str:
    if skill_name == "summary-composer":
        return "builtin-v1"

    skill_dir = SKILLS_ROOT / skill_name
    digest = hashlib.sha256()
    for relative_path in SKILL_FILES.get(skill_name, ["SKILL.md"]):
        path = skill_dir / relative_path
        if path.exists():
            digest.update(path.read_bytes())
    return digest.hexdigest()[:12] or "missing"


def _compute_prompt_version(skill_name: str) -> str:
    prompt_file = PROMPT_FILES.get(skill_name)
    if prompt_file is None:
        return "builtin-v1"

    path = PROMPTS_ROOT / prompt_file
    if not path.exists():
        return "missing"

    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()[:12]
