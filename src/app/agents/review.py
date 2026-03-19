from dataclasses import dataclass

from src.app.agents.base import dedupe, load_prompt
from src.app.contracts.agent_results import ImplementationResult, RepoContextResult, ReviewResult, TestStrategyResult
from src.app.contracts.requests import BaseWorkflowRequest


def run_review_agent(
    request: BaseWorkflowRequest,
    primary_intent: str,
    repo_context: RepoContextResult,
    implementation: ImplementationResult | None,
    test_strategy: TestStrategyResult | None,
) -> ReviewResult:
    missing_evidence: list[str] = []
    if not repo_context.evidence:
        missing_evidence.append("repository evidence 가 없어 영향 범위 확신이 낮다.")
    diff_text = getattr(request, "diff_text", None)
    if primary_intent == "review" and not request.artifacts.changed_files and not diff_text:
        missing_evidence.append("review 요청이지만 changed_files 또는 diff_text 가 없어 실제 변경 범위를 특정하기 어렵다.")

    hidden_dependencies = dedupe(repo_context.dependency_summary)
    regression_risks = list(implementation.risks[:3] if implementation else [])
    security_flags: list[str] = []
    performance_flags: list[str] = []
    compatibility_flags: list[str] = []

    lowered = request.task_text.lower()
    if any(keyword in lowered for keyword in ("auth", "token", "secret", "password", "permission")):
        security_flags.append("인증/권한 관련 변경이면 민감정보 노출과 scope 검증을 함께 확인해야 한다.")
    if any(keyword in lowered for keyword in ("async", "batch", "cache", "latency", "성능")):
        performance_flags.append("성능 민감 경로일 수 있어 latency 와 캐시 영향 점검이 필요하다.")
    if any(keyword in lowered for keyword in ("api", "dto", "schema", "client", "field", "필드")):
        compatibility_flags.append("공개 계약 또는 클라이언트 payload 호환성 검토가 필요하다.")

    if test_strategy is None:
        regression_risks.append("테스트 전략이 없어 회귀 범위가 충분히 검증되지 않았다.")

    readiness_verdict = "ready"
    if missing_evidence:
        readiness_verdict = "blocked"
    elif regression_risks or compatibility_flags or security_flags:
        readiness_verdict = "needs_changes"

    confidence = "high" if repo_context.evidence and not missing_evidence else "medium"
    if not repo_context.evidence:
        confidence = "low"

    return ReviewResult(
        missing_evidence=dedupe(missing_evidence),
        hidden_dependencies=hidden_dependencies,
        regression_risks=dedupe(regression_risks),
        security_flags=dedupe(security_flags),
        performance_flags=dedupe(performance_flags),
        compatibility_flags=dedupe(compatibility_flags),
        readiness_verdict=readiness_verdict,
        confidence=confidence,
    )


@dataclass
class ReviewAgentConfig:
    prompt_file: str = "review.md"


def get_review_prompt() -> str:
    return load_prompt(ReviewAgentConfig.prompt_file)
