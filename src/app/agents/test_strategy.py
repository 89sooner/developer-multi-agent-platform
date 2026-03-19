from dataclasses import dataclass

from src.app.agents.base import dedupe, load_prompt
from src.app.contracts.agent_results import ImplementationResult, RepoContextResult, TestStrategyResult
from src.app.contracts.requests import BaseWorkflowRequest


def run_test_strategy_agent(
    request: BaseWorkflowRequest,
    primary_intent: str,
    repo_context: RepoContextResult | None,
    implementation: ImplementationResult | None,
) -> TestStrategyResult:
    targets = implementation.target_modules if implementation else repo_context.related_files if repo_context else []
    focus = targets[:3] or ["핵심 변경 경로"]

    if primary_intent == "bugfix":
        unit_tests = ["재현 조건 단위 테스트", "중복/예외 처리 분기 테스트"]
        integration_tests = ["문제 발생 API 또는 service 경로 통합 테스트"]
        regression_targets = ["기존 성공 경로 유지", "동시성 또는 재시도 경로 확인"]
        edge_cases = ["중복 요청", "부분 실패 후 재시도", "순서가 뒤바뀐 이벤트 입력"]
    elif primary_intent == "refactor":
        unit_tests = ["분리된 모듈 경계 테스트", "호환성 레이어 테스트"]
        integration_tests = ["기존 호출자와 신규 경계 간 통합 테스트"]
        regression_targets = ["기존 서비스 동작 동일성 확인", "의존성 주입 경로 확인"]
        edge_cases = ["순환 의존성", "초기화 순서", "부분 전환 상태"]
    else:
        unit_tests = ["입력 검증 테스트", "계약/변환 로직 테스트"]
        integration_tests = ["API 또는 주요 service 경로 통합 테스트"]
        regression_targets = ["기존 호출자 호환성 확인", "문서화된 기존 시나리오 유지"]
        edge_cases = ["누락 필드", "잘못된 enum 또는 format", "legacy payload"]

    if focus:
        regression_targets.insert(0, f"주요 검증 대상: {', '.join(focus)}")

    return TestStrategyResult(
        unit_tests=dedupe(unit_tests),
        integration_tests=dedupe(integration_tests),
        regression_targets=dedupe(regression_targets),
        edge_cases=dedupe(edge_cases),
        execution_order=["unit tests", "integration tests", "regression tests"],
        confidence="medium" if targets else "low",
    )


@dataclass
class TestStrategyAgentConfig:
    prompt_file: str = "test_strategy.md"


def get_test_strategy_prompt() -> str:
    return load_prompt(TestStrategyAgentConfig.prompt_file)
