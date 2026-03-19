from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from src.app.agents.implementation import run_implementation_agent
from src.app.agents.orchestrator import classify_request
from src.app.agents.repo_context import run_repo_context_agent
from src.app.agents.requirements import run_requirements_agent
from src.app.agents.review import run_review_agent
from src.app.agents.summary import (
    compose_plan_response,
    compose_review_response,
    compose_test_plan_response,
)
from src.app.agents.test_strategy import run_test_strategy_agent
from src.app.contracts.agent_results import (
    ImplementationResult,
    IntentClassification,
    RepoContextResult,
    RequirementsResult,
    ReviewResult,
    TestStrategyResult,
)
from src.app.contracts.requests import FeedbackRequest, PlanRequest, ReviewRequest, TestPlanRequest
from src.app.contracts.responses import (
    FeedbackResponse,
    RunDetailResponse,
    TestPlanResponse,
    ToolCallRecord,
    TraceResponse,
    TraceStep,
)
from src.app.core.auth import UserContext
from src.app.core.config import get_settings
from src.app.core.policy import enforce_repo_scope, require_approval
from src.app.core.tracing import TraceRecorder
from src.app.services.skill_registry import resolve_skill_versions
from src.app.storage.repositories import store


@dataclass
class WorkflowService:
    def _new_ids(self) -> tuple[str, str]:
        run_id = f"run_{uuid4().hex[:8]}"
        trace_id = f"trace_{uuid4().hex[:8]}"
        return run_id, trace_id

    @staticmethod
    def _fallback_requirements(request: PlanRequest, reason: str) -> RequirementsResult:
        return RequirementsResult(
            feature_summary=request.task_text,
            assumptions=[f"requirements 단계 실패: {reason}"],
            acceptance_criteria=[],
            non_goals=[],
            impacted_areas=[],
            confidence="low",
        )

    @staticmethod
    def _fallback_repo_context(reason: str) -> RepoContextResult:
        return RepoContextResult(
            related_files=[],
            relevant_docs=[],
            similar_implementations=[],
            dependency_summary=[],
            uncertainty_list=[f"repo context 단계 실패: {reason}"],
            evidence=[],
            confidence="low",
        )

    @staticmethod
    def _fallback_implementation(reason: str) -> ImplementationResult:
        return ImplementationResult(
            change_plan=[f"implementation 단계 실패로 구체 계획을 생성하지 못했다: {reason}"],
            target_modules=[],
            api_changes=[],
            data_model_changes=[],
            migration_needs=[],
            rollback_notes=["실패 원인을 확인하기 전까지 실제 변경을 보류한다."],
            risks=["구현 계획 근거가 부족하다."],
            confidence="low",
        )

    @staticmethod
    def _fallback_test_strategy(reason: str) -> TestStrategyResult:
        return TestStrategyResult(
            unit_tests=[],
            integration_tests=[],
            regression_targets=[],
            edge_cases=[f"test strategy 단계 실패: {reason}"],
            execution_order=["unit tests", "integration tests", "regression tests"],
            confidence="low",
        )

    @staticmethod
    def _fallback_review(reason: str) -> ReviewResult:
        return ReviewResult(
            missing_evidence=[f"review 단계 실패: {reason}"],
            hidden_dependencies=[],
            regression_risks=["최종 검토가 완료되지 않았다."],
            security_flags=[],
            performance_flags=[],
            compatibility_flags=[],
            readiness_verdict="blocked",
            confidence="low",
        )

    def _execute_step(self, tracer: TraceRecorder, step_name: str, input_ref: str, callback, fallback_builder, warnings: list[str]):
        handle = tracer.start_step(step_name, input_ref=input_ref)
        try:
            result = callback()
            tracer.finish_step(
                handle,
                status="completed",
                confidence=getattr(result, "confidence", None),
                output_ref=f"{step_name}_result",
            )
            return result
        except Exception as exc:
            warnings.append(f"{step_name} 단계가 실패해 degraded mode 로 응답했다: {exc}")
            fallback = fallback_builder(str(exc))
            tracer.finish_step(
                handle,
                status="failed",
                confidence=getattr(fallback, "confidence", "low"),
                output_ref=f"{step_name}_fallback",
                error_message=str(exc),
            )
            return fallback

    def _start_run(
        self,
        *,
        run_id: str,
        trace_id: str,
        request,
        user: UserContext,
        classification: IntentClassification,
        skill_versions: dict[str, str],
    ) -> None:
        settings = get_settings()
        store.upsert_run(
            {
                "run_id": run_id,
                "status": "running",
                "created_at": store.now(),
                "completed_at": None,
                "request_type": classification.primary_intent,
                "primary_intent": classification.primary_intent,
                "secondary_intents": classification.secondary_intents,
                "selected_agents": classification.selected_agents,
                "user_id": user.user_id,
                "repo_scope": user.repo_scopes,
                "model_version": settings.openai_model,
                "skill_versions": skill_versions,
                "request": request.model_dump(),
                "result": None,
                "trace_id": trace_id,
            }
        )

    def _finish_run(
        self,
        *,
        run_id: str,
        trace_id: str,
        request,
        user: UserContext,
        classification: IntentClassification,
        skill_versions: dict[str, str],
        result,
        tracer: TraceRecorder,
    ) -> None:
        store.upsert_run(
            {
                "run_id": run_id,
                "status": "completed",
                "created_at": store.get_run(run_id)["created_at"],
                "completed_at": store.now(),
                "request_type": classification.primary_intent,
                "primary_intent": classification.primary_intent,
                "secondary_intents": classification.secondary_intents,
                "selected_agents": classification.selected_agents,
                "user_id": user.user_id,
                "repo_scope": user.repo_scopes,
                "model_version": get_settings().openai_model,
                "skill_versions": skill_versions,
                "request": request.model_dump(),
                "result": result.model_dump(),
                "trace_id": trace_id,
            }
        )
        store.save_trace(run_id, trace_id, tracer.export_payload())

    def _run_orchestrator(self, request: PlanRequest | ReviewRequest, *, forced_intent=None) -> tuple[IntentClassification, TraceRecorder, str, str]:
        run_id, trace_id = self._new_ids()
        tracer = TraceRecorder(run_id=run_id, trace_id=trace_id)
        handle = tracer.start_step("orchestrator", input_ref="request")
        classification = classify_request(request, forced_intent=forced_intent)
        tracer.finish_step(
            handle,
            status="completed",
            confidence=classification.confidence,
            output_ref="intent_classification",
        )
        return classification, tracer, run_id, trace_id

    def _base_warnings(self, repo_id: str) -> list[str]:
        warnings: list[str] = []
        workspace_name = Path.cwd().name
        if repo_id != workspace_name:
            warnings.append(
                f"현재 local connector 는 workspace mirror({workspace_name}) 를 기준으로 근거를 수집했다."
            )
        return warnings

    def create_plan(self, request: PlanRequest, user: UserContext):
        enforce_repo_scope(user, request.repo_id)
        require_approval(request.options.write_actions, request.options.approval_token)

        classification, tracer, run_id, trace_id = self._run_orchestrator(request)
        skill_versions = resolve_skill_versions(classification.selected_agents)
        self._start_run(
            run_id=run_id,
            trace_id=trace_id,
            request=request,
            user=user,
            classification=classification,
            skill_versions=skill_versions,
        )

        warnings = self._base_warnings(request.repo_id)
        requirements = self._execute_step(
            tracer,
            "requirements",
            "request",
            lambda: run_requirements_agent(request, classification.primary_intent),
            lambda reason: self._fallback_requirements(request, reason),
            warnings,
        )
        repo_context = self._execute_step(
            tracer,
            "repo_context",
            "requirements_result",
            lambda: run_repo_context_agent(request, tracer=tracer),
            self._fallback_repo_context,
            warnings,
        )
        implementation = self._execute_step(
            tracer,
            "implementation",
            "repo_context_result",
            lambda: run_implementation_agent(request, classification.primary_intent, requirements, repo_context),
            self._fallback_implementation,
            warnings,
        )
        test_strategy: TestStrategyResult | None = None
        if "test-strategy-generator" in classification.selected_agents:
            test_strategy = self._execute_step(
                tracer,
                "test_strategy",
                "implementation_result",
                lambda: run_test_strategy_agent(request, classification.primary_intent, repo_context, implementation),
                self._fallback_test_strategy,
                warnings,
            )

        review = self._execute_step(
            tracer,
            "review",
            "implementation_result",
            lambda: run_review_agent(request, classification.primary_intent, repo_context, implementation, test_strategy),
            self._fallback_review,
            warnings,
        )
        handle = tracer.start_step("summary", input_ref="review_result")
        result = compose_plan_response(
            run_id=run_id,
            trace_id=trace_id,
            classification=classification,
            requirements=requirements,
            repo_context=repo_context,
            implementation=implementation,
            test_strategy=test_strategy,
            review=review,
            model_version=get_settings().openai_model,
            skill_versions=skill_versions,
            warnings=warnings,
        )
        tracer.finish_step(
            handle,
            status="completed",
            confidence=result.confidence,
            output_ref="plan_response",
        )
        self._finish_run(
            run_id=run_id,
            trace_id=trace_id,
            request=request,
            user=user,
            classification=classification,
            skill_versions=skill_versions,
            result=result,
            tracer=tracer,
        )
        return result

    def create_review(self, request: ReviewRequest, user: UserContext):
        enforce_repo_scope(user, request.repo_id)
        require_approval(request.options.write_actions, request.options.approval_token)

        classification, tracer, run_id, trace_id = self._run_orchestrator(request, forced_intent="review")
        skill_versions = resolve_skill_versions(classification.selected_agents)
        self._start_run(
            run_id=run_id,
            trace_id=trace_id,
            request=request,
            user=user,
            classification=classification,
            skill_versions=skill_versions,
        )

        warnings = self._base_warnings(request.repo_id)
        repo_context = self._execute_step(
            tracer,
            "repo_context",
            "request",
            lambda: run_repo_context_agent(request, tracer=tracer),
            self._fallback_repo_context,
            warnings,
        )
        test_strategy = self._execute_step(
            tracer,
            "test_strategy",
            "repo_context_result",
            lambda: run_test_strategy_agent(request, classification.primary_intent, repo_context, None),
            self._fallback_test_strategy,
            warnings,
        )
        review = self._execute_step(
            tracer,
            "review",
            "test_strategy_result",
            lambda: run_review_agent(request, classification.primary_intent, repo_context, None, test_strategy),
            self._fallback_review,
            warnings,
        )
        handle = tracer.start_step("summary", input_ref="review_result")
        result = compose_review_response(
            run_id=run_id,
            trace_id=trace_id,
            classification=classification,
            repo_context=repo_context,
            review=review,
            test_strategy=test_strategy,
            model_version=get_settings().openai_model,
            skill_versions=skill_versions,
            warnings=warnings,
        )
        tracer.finish_step(
            handle,
            status="completed",
            confidence=result.confidence,
            output_ref="review_response",
        )
        self._finish_run(
            run_id=run_id,
            trace_id=trace_id,
            request=request,
            user=user,
            classification=classification,
            skill_versions=skill_versions,
            result=result,
            tracer=tracer,
        )
        return result

    def create_test_plan(self, request: TestPlanRequest, user: UserContext) -> TestPlanResponse:
        enforce_repo_scope(user, request.repo_id)

        run_id, trace_id = self._new_ids()
        tracer = TraceRecorder(run_id=run_id, trace_id=trace_id)
        classification = IntentClassification(
            primary_intent="test_plan",
            secondary_intents=[],
            selected_agents=["workflow-orchestrator", "test-strategy-generator"],
            warnings=[],
            confidence="high",
        )
        skill_versions = resolve_skill_versions(classification.selected_agents)

        class SyntheticTestPlanRequest:
            def __init__(self, payload: TestPlanRequest) -> None:
                self.repo_id = payload.repo_id
                self.branch = payload.branch
                self.task_text = " ".join(payload.implementation_plan + payload.impacted_areas)
                self.request_type = "test_plan"
                self.options = type("Options", (), {"include_tests": True, "write_actions": [], "approval_token": None})()
                self.artifacts = type("Artifacts", (), {"issue_ids": [], "changed_files": [], "pr_url": None})()

        synthetic_request = SyntheticTestPlanRequest(request)
        handle = tracer.start_step("orchestrator", input_ref="request")
        tracer.finish_step(handle, status="completed", confidence="high", output_ref="intent_classification")
        self._start_run(
            run_id=run_id,
            trace_id=trace_id,
            request=request,
            user=user,
            classification=classification,
            skill_versions=skill_versions,
        )

        warnings = self._base_warnings(request.repo_id)
        test_strategy = self._execute_step(
            tracer,
            "test_strategy",
            "request",
            lambda: run_test_strategy_agent(synthetic_request, "test_plan", None, None),
            self._fallback_test_strategy,
            warnings,
        )
        summary_handle = tracer.start_step("summary", input_ref="test_strategy_result")
        result = compose_test_plan_response(
            run_id=run_id,
            trace_id=trace_id,
            classification=classification,
            test_strategy=test_strategy,
            model_version=get_settings().openai_model,
            skill_versions=skill_versions,
            warnings=warnings,
        )
        tracer.finish_step(summary_handle, status="completed", confidence=result.confidence, output_ref="test_plan_response")
        self._finish_run(
            run_id=run_id,
            trace_id=trace_id,
            request=request,
            user=user,
            classification=classification,
            skill_versions=skill_versions,
            result=result,
            tracer=tracer,
        )
        return result

    def get_run(self, run_id: str, user: UserContext) -> RunDetailResponse | None:
        item = store.get_run(run_id)
        if item is None:
            return None
        if item["user_id"] != user.user_id and "admin" not in user.roles:
            raise PermissionError("run access forbidden")
        return RunDetailResponse(**item)

    def get_trace(self, run_id: str, user: UserContext) -> TraceResponse | None:
        run_item = store.get_run(run_id)
        if run_item is None:
            return None
        if run_item["user_id"] != user.user_id and "admin" not in user.roles:
            raise PermissionError("trace access forbidden")

        item = store.get_trace(run_id)
        if item is None:
            return None
        steps = [TraceStep(**step) for step in item["steps"]]
        tool_calls = [ToolCallRecord(**call) for call in item.get("tool_calls", [])]
        return TraceResponse(
            trace_id=item["trace_id"],
            steps=steps,
            spans=steps,
            tool_calls=tool_calls,
            exported_at=item.get("exported_at"),
            error_summary=item.get("error_summary"),
        )

    def create_feedback(self, request: FeedbackRequest, user: UserContext) -> FeedbackResponse:
        run_item = store.get_run(request.run_id)
        if run_item is None:
            raise ValueError("run not found")
        if run_item["user_id"] != user.user_id and "admin" not in user.roles:
            raise PermissionError("feedback access forbidden")

        feedback_id = f"fb_{uuid4().hex[:8]}"
        store.save_feedback(feedback_id, request.model_dump())
        return FeedbackResponse(feedback_id=feedback_id, stored=True)


workflow_service = WorkflowService()
