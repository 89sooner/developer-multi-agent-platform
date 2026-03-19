from typing import Any, Literal

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["low", "medium", "high"]
RunStatus = Literal["queued", "running", "completed", "failed"]


class Evidence(BaseModel):
    source_type: str
    source_id: str | None = None
    locator: str
    snippet: str | None = None
    timestamp: str | None = None
    confidence: ConfidenceLevel = "medium"


class BaseWorkflowResponse(BaseModel):
    run_id: str
    status: RunStatus
    trace_id: str
    request_type: str
    confidence: ConfidenceLevel = "medium"


class PlanResponse(BaseWorkflowResponse):
    summary: str
    impacted_areas: list[str]
    implementation_plan: list[str]
    tests: list[str]
    risks: list[str]
    open_questions: list[str]
    evidence: list[Evidence]


class ReviewFinding(BaseModel):
    category: str
    severity: ConfidenceLevel
    message: str
    evidence: list[Evidence] = Field(default_factory=list)


class ReviewResponse(BaseWorkflowResponse):
    summary: str
    review_findings: list[ReviewFinding]
    missing_tests: list[str]
    risks: list[str]
    readiness_verdict: Literal["ready", "needs_changes", "blocked"]
    evidence: list[Evidence]


class TestPlanResponse(BaseWorkflowResponse):
    unit_tests: list[str]
    integration_tests: list[str]
    regression_targets: list[str]
    edge_cases: list[str]
    execution_order: list[str]


class RunDetailResponse(BaseModel):
    run_id: str
    status: str
    created_at: str
    completed_at: str | None = None
    request: dict[str, Any]
    result: dict[str, Any]
    trace_id: str


class TraceStep(BaseModel):
    step_name: str
    status: str
    latency_ms: int
    tool_calls: int
    error_message: str | None = None


class TraceResponse(BaseModel):
    trace_id: str
    steps: list[TraceStep]
    error_summary: str | None = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    stored: bool
