from dataclasses import dataclass
import re

from src.app.agents.base import dedupe, load_prompt
from src.app.contracts.agent_results import RequirementsResult
from src.app.contracts.requests import BaseWorkflowRequest


def run_requirements_agent(request: BaseWorkflowRequest, primary_intent: str) -> RequirementsResult:
    summary = request.task_text.strip()
    summary = re.split(r"[.!?\n]", summary)[0].strip() or "개발 요청을 구현 가능한 작업으로 정리한다."

    assumptions: list[str] = []
    if "기본값" in request.task_text or "default" in request.task_text.lower():
        assumptions.append("기본값 정책이 명확한지 확인이 필요하다.")
    if "api" in request.task_text.lower():
        assumptions.append("기존 API 소비자와의 호환성 확인이 필요하다.")
    if primary_intent == "bugfix":
        assumptions.append("재현 조건과 로그 기준이 충분한지 확인이 필요하다.")
    if primary_intent == "refactor":
        assumptions.append("기존 동작을 유지해야 하는 범위를 먼저 확정해야 한다.")

    if primary_intent == "feature":
        acceptance_criteria = [
            "요청한 기능 변경이 관련 입력/출력 경로에 반영된다.",
            "검증 규칙과 문서가 변경 사항과 일치한다.",
            "기존 호출자에 대한 호환성 영향이 명시된다.",
        ]
        non_goals = ["실제 코드 배포 자동화", "승인 없는 외부 시스템 쓰기"]
    elif primary_intent == "bugfix":
        acceptance_criteria = [
            "문제를 재현할 수 있는 조건이 정의된다.",
            "수정 이후 동일 증상이 재발하지 않도록 회귀 포인트가 정리된다.",
            "부작용 가능 경로가 함께 검토된다.",
        ]
        non_goals = ["관련 없는 구조 개편", "근거 없는 성능 최적화"]
    else:
        acceptance_criteria = [
            "변경 전후 경계와 책임이 분명해진다.",
            "단계적 전환 경로와 롤백 방법이 존재한다.",
            "기존 동작 유지 범위가 테스트 가능하게 정리된다.",
        ]
        non_goals = ["동시에 여러 시스템을 전면 개편하는 작업"]

    impacted_areas: list[str] = []
    lowered = request.task_text.lower()
    for keyword, area in (
        ("api", "api layer"),
        ("dto", "schema layer"),
        ("schema", "schema layer"),
        ("service", "service layer"),
        ("문서", "documentation"),
        ("docs", "documentation"),
        ("test", "test suite"),
        ("validation", "validation path"),
        ("client", "client integration"),
    ):
        if keyword in lowered:
            impacted_areas.append(area)

    field_match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*(필드|field)", request.task_text)
    if field_match:
        impacted_areas.append(f"{field_match.group(1)} contract")

    impacted_areas = dedupe(impacted_areas)
    confidence = "medium" if impacted_areas else "low"
    return RequirementsResult(
        feature_summary=summary,
        assumptions=dedupe(assumptions),
        acceptance_criteria=acceptance_criteria,
        non_goals=non_goals,
        impacted_areas=impacted_areas,
        confidence=confidence,
    )


@dataclass
class RequirementsAgentConfig:
    prompt_file: str = "requirements.md"


def get_requirements_prompt() -> str:
    return load_prompt(RequirementsAgentConfig.prompt_file)
