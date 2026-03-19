from dataclasses import dataclass

from src.app.agents.base import dedupe, load_prompt
from src.app.contracts.agent_results import IntentClassification
from src.app.contracts.requests import BaseWorkflowRequest, RequestType

INTENT_KEYWORDS: dict[RequestType, tuple[str, ...]] = {
    "feature": ("추가", "구현", "지원", "신규", "feature", "add", "introduce"),
    "bugfix": ("버그", "오류", "실패", "중복", "fix", "bug", "error", "retry", "race"),
    "refactor": ("리팩터링", "분리", "정리", "모듈화", "refactor", "cleanup", "split"),
    "review": ("리뷰", "review", "pr", "diff", "코멘트", "누락 테스트"),
    "test_plan": ("테스트 계획", "test plan", "test strategy", "qa", "시나리오"),
}


def _score_intents(task_text: str) -> dict[RequestType, int]:
    lowered = task_text.lower()
    scores: dict[RequestType, int] = {intent: 0 for intent in INTENT_KEYWORDS}
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lowered:
                scores[intent] += 2
    return scores


def classify_request(
    request: BaseWorkflowRequest,
    *,
    forced_intent: RequestType | None = None,
) -> IntentClassification:
    scores = _score_intents(request.task_text)
    warnings: list[str] = []

    if request.request_type is not None:
        scores[request.request_type] += 5
    if forced_intent is not None:
        scores[forced_intent] += 6

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary_intent = ranked[0][0] if ranked[0][1] > 0 else (forced_intent or request.request_type or "feature")
    secondary_intents = [intent for intent, score in ranked[1:] if score > 0 and intent != primary_intent]

    if request.request_type and request.request_type != primary_intent:
        warnings.append(
            f"request_type={request.request_type} 요청이 있었지만 task_text 기반 분류는 {primary_intent} 에 더 가깝다."
        )

    selected_agents = ["workflow-orchestrator"]
    if primary_intent in {"feature", "bugfix", "refactor"}:
        selected_agents.extend(["requirements-planner", "repo-context-finder", "implementation-planner"])
        if request.options.include_tests:
            selected_agents.append("test-strategy-generator")
        selected_agents.extend(["review-gate", "summary-composer"])
    elif primary_intent == "review":
        selected_agents.extend(["repo-context-finder", "test-strategy-generator", "review-gate", "summary-composer"])
    else:
        selected_agents.extend(["test-strategy-generator"])

    selected_agents = dedupe(selected_agents)
    confidence = "high" if ranked[0][1] >= 5 else "medium"
    if ranked[0][1] == 0:
        confidence = "low"
        warnings.append("task_text 단서가 약해 기본 intent 분류를 사용했다.")

    return IntentClassification(
        primary_intent=primary_intent,
        secondary_intents=secondary_intents,
        selected_agents=selected_agents,
        warnings=warnings,
        confidence=confidence,
    )


@dataclass
class OrchestratorConfig:
    prompt_file: str = "orchestrator.md"


def get_orchestrator_prompt() -> str:
    return load_prompt(OrchestratorConfig.prompt_file)
