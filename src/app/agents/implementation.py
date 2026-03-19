from dataclasses import dataclass

from src.app.agents.base import dedupe, load_prompt
from src.app.contracts.agent_results import ImplementationResult, RepoContextResult, RequirementsResult
from src.app.contracts.requests import BaseWorkflowRequest


def run_implementation_agent(
    request: BaseWorkflowRequest,
    primary_intent: str,
    requirements: RequirementsResult,
    repo_context: RepoContextResult,
) -> ImplementationResult:
    target_modules = dedupe(repo_context.related_files[:5] + requirements.impacted_areas[:3])
    change_plan: list[str] = []
    api_changes: list[str] = []
    data_model_changes: list[str] = []
    migration_needs: list[str] = []
    rollback_notes: list[str] = []
    risks: list[str] = []

    lowered = request.task_text.lower()
    mentions_schema = any(keyword in lowered for keyword in ("field", "필드", "schema", "dto", "model"))
    mentions_api = "api" in lowered or "endpoint" in lowered

    if primary_intent == "bugfix":
        change_plan.extend(
            [
                "재현 조건과 실패 경로를 먼저 고정한다.",
                "관련 모듈에서 중복 처리 또는 예외 처리 지점을 식별한다.",
                "수정 후 회귀 테스트와 관측 포인트를 추가한다.",
            ]
        )
        risks.extend(["재현 조건이 불완전하면 원인과 다른 지점을 수정할 수 있다."])
    elif primary_intent == "refactor":
        change_plan.extend(
            [
                "현재 호출 경로와 경계 책임을 먼저 문서화한다.",
                "호환성 레이어를 두고 단계적으로 호출자를 이동한다.",
                "최종 정리 전에 회귀 테스트와 롤백 지점을 확인한다.",
            ]
        )
        risks.extend(["숨은 결합도가 높으면 단계적 분리 없이 회귀가 발생할 수 있다."])
    else:
        change_plan.extend(
            [
                "입력/출력 계약과 validation 경로를 먼저 수정한다.",
                "서비스 및 저장 경로에 변경을 반영한다.",
                "문서와 호출자 영향을 함께 정리한다.",
            ]
        )
        risks.extend(["공개 계약 변경 시 기존 호출자와의 호환성 문제가 생길 수 있다."])

    if target_modules:
        change_plan.insert(0, f"우선 검토 대상: {', '.join(target_modules[:3])}")

    if mentions_api:
        api_changes.append("API request/response 계약 변경 여부를 확인한다.")
        rollback_notes.append("기존 API 계약으로 빠르게 되돌릴 수 있는 fallback 경로를 남긴다.")
    if mentions_schema:
        data_model_changes.append("계약 모델과 validation 스키마 변경 가능성이 있다.")
        migration_needs.append("필드 추가가 저장소 스키마에 닿는지 확인한다.")
        rollback_notes.append("새 필드 사용 로직을 제거해도 기존 payload 가 동작하는지 확인한다.")
    if repo_context.uncertainty_list:
        risks.extend(repo_context.uncertainty_list[:2])

    confidence = "high" if repo_context.evidence and len(target_modules) >= 2 else "medium"
    if not repo_context.evidence:
        confidence = "low"

    return ImplementationResult(
        change_plan=dedupe(change_plan),
        target_modules=target_modules,
        api_changes=dedupe(api_changes),
        data_model_changes=dedupe(data_model_changes),
        migration_needs=dedupe(migration_needs),
        rollback_notes=dedupe(rollback_notes or ["핵심 계약 변경이 포함되면 이전 동작으로 되돌릴 기준을 남긴다."]),
        risks=dedupe(risks),
        confidence=confidence,
    )


@dataclass
class ImplementationAgentConfig:
    prompt_file: str = "implementation.md"


def get_implementation_prompt() -> str:
    return load_prompt(ImplementationAgentConfig.prompt_file)
