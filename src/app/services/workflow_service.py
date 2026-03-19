from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import uuid4

from src.app.agents.implementation import get_implementation_prompt
from src.app.agents.orchestrator import get_orchestrator_prompt
from src.app.agents.repo_context import get_repo_context_prompt
from src.app.agents.review import get_review_prompt
from src.app.agents.test_strategy import get_test_strategy_prompt
from src.app.contracts.requests import FeedbackRequest, PlanRequest, ReviewRequest, TestPlanRequest
from src.app.contracts.responses import (
    Evidence,
    FeedbackResponse,
    PlanResponse,
    ReviewFinding,
    ReviewResponse,
    RunDetailResponse,
    TestPlanResponse,
    TraceResponse,
    TraceStep,
)
from src.app.storage.repositories import store
from src.app.tools.ci_lookup import lookup_ci
from src.app.tools.docs_search import search_docs
from src.app.tools.issue_lookup import lookup_issues
from src.app.tools.repo_search import search_repo


@dataclass
class WorkflowService:
    def _new_ids(self) -> tuple[str, str]:
        run_id = f"run_{uuid4().hex[:8]}"
        trace_id = f"trace_{uuid4().hex[:8]}"
        return run_id, trace_id

    def _collect_stub_evidence(self, request: PlanRequest | ReviewRequest) -> list[Evidence]:
        evidence = []
        evidence.extend(search_repo(request.repo_id, request.branch, request.task_text))
        evidence.extend(search_docs(request.repo_id, request.task_text))
        if request.artifacts.issue_ids:
            evidence.extend(lookup_issues(request.artifacts.issue_ids))
        evidence.extend(lookup_ci(request.repo_id, request.branch))
        return evidence

    def create_plan(self, request: PlanRequest) -> PlanResponse:
        run_id, trace_id = self._new_ids()
        evidence = self._collect_stub_evidence(request)

        response = PlanResponse(
            run_id=run_id,
            status="completed",
            trace_id=trace_id,
            request_type=request.request_type,
            summary="요청을 처리하기 위한 영향 범위와 구현 계획 초안이다.",
            impacted_areas=["api layer", "service layer", "schema layer"],
            implementation_plan=[
                "관련 DTO와 validation path 확인",
                "저장/조회 경로 수정",
                "호환성 검토 후 문서 업데이트",
            ],
            tests=(
                [
                    "정상 입력 단위 테스트",
                    "오류 입력 테스트",
                    "역호환성 회귀 테스트",
                ]
                if request.options.include_tests
                else []
            ),
            risks=[
                "기존 클라이언트와의 호환성 문제",
                "기본값 정책 누락 가능성",
            ],
            open_questions=[
                "기본값을 서버에서 강제할지 여부",
            ],
            evidence=evidence,
            confidence="medium",
        )

        store.runs[run_id] = {
            "run_id": run_id,
            "status": "completed",
            "created_at": store.now(),
            "completed_at": store.now(),
            "request": request.model_dump(),
            "result": response.model_dump(),
            "trace_id": trace_id,
        }
        store.traces[run_id] = {
            "trace_id": trace_id,
            "steps": [
                {"step_name": "orchestrator", "status": "completed", "latency_ms": 120, "tool_calls": 0},
                {"step_name": "repo_context", "status": "completed", "latency_ms": 220, "tool_calls": 4},
                {"step_name": "implementation", "status": "completed", "latency_ms": 180, "tool_calls": 0},
                {"step_name": "review", "status": "completed", "latency_ms": 160, "tool_calls": 0},
            ],
            "prompts": {
                "orchestrator": get_orchestrator_prompt(),
                "repo_context": get_repo_context_prompt(),
                "implementation": get_implementation_prompt(),
                "review": get_review_prompt(),
            },
        }
        return response

    def create_review(self, request: ReviewRequest) -> ReviewResponse:
        run_id, trace_id = self._new_ids()
        evidence = self._collect_stub_evidence(request)

        response = ReviewResponse(
            run_id=run_id,
            status="completed",
            trace_id=trace_id,
            request_type="review",
            summary="변경안 검토 결과, 추가 검증이 필요한 항목이 있다.",
            review_findings=[
                ReviewFinding(
                    category="compatibility",
                    severity="medium",
                    message="기존 클라이언트와의 역호환성 검증이 더 필요하다.",
                    evidence=evidence[:1],
                ),
                ReviewFinding(
                    category="testing",
                    severity="medium",
                    message="오류 입력 케이스 테스트가 부족하다.",
                    evidence=evidence[1:2],
                ),
            ],
            missing_tests=[
                "invalid input path test",
                "backward compatibility regression",
            ],
            risks=[
                "스키마 변경에 따른 API 호환성 문제",
                "문서 누락 가능성",
            ],
            readiness_verdict="needs_changes",
            evidence=evidence,
            confidence="medium",
        )

        store.runs[run_id] = {
            "run_id": run_id,
            "status": "completed",
            "created_at": store.now(),
            "completed_at": store.now(),
            "request": request.model_dump(),
            "result": response.model_dump(),
            "trace_id": trace_id,
        }
        store.traces[run_id] = {
            "trace_id": trace_id,
            "steps": [
                {"step_name": "orchestrator", "status": "completed", "latency_ms": 100, "tool_calls": 0},
                {"step_name": "repo_context", "status": "completed", "latency_ms": 240, "tool_calls": 4},
                {"step_name": "review", "status": "completed", "latency_ms": 190, "tool_calls": 0},
            ],
            "prompts": {
                "orchestrator": get_orchestrator_prompt(),
                "repo_context": get_repo_context_prompt(),
                "review": get_review_prompt(),
            },
        }
        return response

    def create_test_plan(self, request: TestPlanRequest) -> TestPlanResponse:
        run_id, trace_id = self._new_ids()
        response = TestPlanResponse(
            run_id=run_id,
            status="completed",
            trace_id=trace_id,
            request_type="test_plan",
            unit_tests=["입력 검증 테스트", "도메인 로직 단위 테스트"],
            integration_tests=["API 경로 통합 테스트", "영속성 계층 통합 테스트"],
            regression_targets=["기존 프로필 수정 흐름", "기존 설정 조회 흐름"],
            edge_cases=["null or empty value", "unknown enum value", "legacy client payload"],
            execution_order=[
                "unit tests",
                "integration tests",
                "regression tests",
            ],
            confidence="medium",
        )
        store.runs[run_id] = {
            "run_id": run_id,
            "status": "completed",
            "created_at": store.now(),
            "completed_at": store.now(),
            "request": request.model_dump(),
            "result": response.model_dump(),
            "trace_id": trace_id,
        }
        store.traces[run_id] = {
            "trace_id": trace_id,
            "steps": [
                {"step_name": "orchestrator", "status": "completed", "latency_ms": 90, "tool_calls": 0},
                {"step_name": "test_strategy", "status": "completed", "latency_ms": 180, "tool_calls": 0},
            ],
            "prompts": {
                "orchestrator": get_orchestrator_prompt(),
                "test_strategy": get_test_strategy_prompt(),
            },
        }
        return response

    def get_run(self, run_id: str) -> RunDetailResponse | None:
        item = store.runs.get(run_id)
        if item is None:
            return None
        return RunDetailResponse(**item)

    def get_trace(self, run_id: str) -> TraceResponse | None:
        item = store.traces.get(run_id)
        if item is None:
            return None
        steps = [TraceStep(**step) for step in item["steps"]]
        return TraceResponse(trace_id=item["trace_id"], steps=steps, error_summary=None)

    def create_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        feedback_id = f"fb_{uuid4().hex[:8]}"
        store.feedback[feedback_id] = {
            "feedback_id": feedback_id,
            "payload": request.model_dump(),
            "created_at": store.now(),
        }
        return FeedbackResponse(feedback_id=feedback_id, stored=True)


workflow_service = WorkflowService()
