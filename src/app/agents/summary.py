from __future__ import annotations

from src.app.agents.base import collapse_confidence, dedupe, module_area
from src.app.contracts.agent_results import (
    ImplementationResult,
    IntentClassification,
    RepoContextResult,
    RequirementsResult,
    ReviewResult,
    TestStrategyResult,
)
from src.app.contracts.responses import PlanResponse, ReviewFinding, ReviewResponse, TestPlanResponse


def compose_plan_response(
    *,
    run_id: str,
    trace_id: str,
    classification: IntentClassification,
    requirements: RequirementsResult,
    repo_context: RepoContextResult,
    implementation: ImplementationResult,
    test_strategy: TestStrategyResult | None,
    review: ReviewResult,
    model_version: str,
    skill_versions: dict[str, str],
    warnings: list[str],
) -> PlanResponse:
    impacted_areas = dedupe(
        requirements.impacted_areas
        + [module_area(locator) for locator in repo_context.related_files]
        + implementation.target_modules
    )
    tests = []
    if test_strategy is not None:
        tests = dedupe(test_strategy.unit_tests[:2] + test_strategy.integration_tests[:2] + test_strategy.regression_targets[:2])

    risks = dedupe(
        implementation.risks
        + review.regression_risks
        + review.compatibility_flags
        + review.security_flags
        + review.performance_flags
    )
    open_questions = dedupe(requirements.assumptions + repo_context.uncertainty_list + review.missing_evidence)
    confidence = collapse_confidence(
        [
            classification.confidence,
            requirements.confidence,
            repo_context.confidence,
            implementation.confidence,
            review.confidence,
            test_strategy.confidence if test_strategy else "medium",
        ]
    )

    summary = (
        f"{classification.primary_intent} 요청으로 분류되었고, "
        f"{len(impacted_areas)}개 영향 영역과 {len(repo_context.evidence)}개 근거를 기반으로 계획을 정리했다."
    )
    if not repo_context.evidence:
        summary = "근거가 제한적이어서 low-confidence 계획 초안을 반환한다."

    return PlanResponse(
        run_id=run_id,
        status="completed",
        trace_id=trace_id,
        request_type=classification.primary_intent,
        primary_intent=classification.primary_intent,
        secondary_intents=classification.secondary_intents,
        selected_agents=classification.selected_agents,
        model_version=model_version,
        skill_versions=skill_versions,
        warnings=dedupe(warnings + classification.warnings),
        summary=summary,
        impacted_areas=impacted_areas or ["영향 영역을 특정할 근거가 부족하다."],
        implementation_plan=implementation.change_plan,
        tests=tests,
        risks=risks,
        open_questions=open_questions,
        evidence=repo_context.evidence,
        confidence=confidence,
    )


def compose_review_response(
    *,
    run_id: str,
    trace_id: str,
    classification: IntentClassification,
    repo_context: RepoContextResult,
    review: ReviewResult,
    test_strategy: TestStrategyResult | None,
    model_version: str,
    skill_versions: dict[str, str],
    warnings: list[str],
) -> ReviewResponse:
    findings: list[ReviewFinding] = []
    for category, items, severity in (
        ("missing_evidence", review.missing_evidence, "high"),
        ("dependency", review.hidden_dependencies, "medium"),
        ("regression", review.regression_risks, "medium"),
        ("security", review.security_flags, "high"),
        ("performance", review.performance_flags, "medium"),
        ("compatibility", review.compatibility_flags, "medium"),
    ):
        for message in items:
            findings.append(
                ReviewFinding(
                    category=category,
                    severity=severity,  # type: ignore[arg-type]
                    message=message,
                    evidence=repo_context.evidence[:2],
                )
            )

    missing_tests = []
    if test_strategy is not None:
        missing_tests = dedupe(
            test_strategy.unit_tests[:2] + test_strategy.integration_tests[:2] + test_strategy.edge_cases[:2]
        )

    confidence = collapse_confidence(
        [
            classification.confidence,
            repo_context.confidence,
            review.confidence,
            test_strategy.confidence if test_strategy else "medium",
        ]
    )
    summary = (
        f"review verdict={review.readiness_verdict}. "
        f"{len(findings)}개 점검 항목과 {len(repo_context.evidence)}개 근거를 반환한다."
    )
    return ReviewResponse(
        run_id=run_id,
        status="completed",
        trace_id=trace_id,
        request_type="review",
        primary_intent=classification.primary_intent,
        secondary_intents=classification.secondary_intents,
        selected_agents=classification.selected_agents,
        model_version=model_version,
        skill_versions=skill_versions,
        warnings=dedupe(warnings + classification.warnings),
        summary=summary,
        review_findings=findings,
        missing_tests=missing_tests,
        risks=dedupe(review.regression_risks + review.compatibility_flags + review.security_flags + review.performance_flags),
        readiness_verdict=review.readiness_verdict,  # type: ignore[arg-type]
        evidence=repo_context.evidence,
        confidence=confidence,
    )


def compose_test_plan_response(
    *,
    run_id: str,
    trace_id: str,
    classification: IntentClassification,
    test_strategy: TestStrategyResult,
    model_version: str,
    skill_versions: dict[str, str],
    warnings: list[str],
) -> TestPlanResponse:
    return TestPlanResponse(
        run_id=run_id,
        status="completed",
        trace_id=trace_id,
        request_type="test_plan",
        primary_intent=classification.primary_intent,
        secondary_intents=classification.secondary_intents,
        selected_agents=classification.selected_agents,
        model_version=model_version,
        skill_versions=skill_versions,
        warnings=warnings,
        unit_tests=test_strategy.unit_tests,
        integration_tests=test_strategy.integration_tests,
        regression_targets=test_strategy.regression_targets,
        edge_cases=test_strategy.edge_cases,
        execution_order=test_strategy.execution_order,
        confidence=test_strategy.confidence,
    )
