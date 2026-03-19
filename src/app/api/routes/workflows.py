from fastapi import APIRouter, HTTPException

from src.app.contracts.requests import PlanRequest, ReviewRequest, TestPlanRequest
from src.app.contracts.responses import (
    PlanResponse,
    ReviewResponse,
    RunDetailResponse,
    TestPlanResponse,
    TraceResponse,
)
from src.app.services.workflow_service import workflow_service

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
def create_plan(request: PlanRequest) -> PlanResponse:
    return workflow_service.create_plan(request)


@router.post("/review", response_model=ReviewResponse)
def create_review(request: ReviewRequest) -> ReviewResponse:
    return workflow_service.create_review(request)


@router.post("/test-plan", response_model=TestPlanResponse)
def create_test_plan(request: TestPlanRequest) -> TestPlanResponse:
    return workflow_service.create_test_plan(request)


@router.get("/{run_id}", response_model=RunDetailResponse)
def get_run(run_id: str) -> RunDetailResponse:
    result = workflow_service.get_run(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="run not found")
    return result


@router.get("/{run_id}/trace", response_model=TraceResponse)
def get_trace(run_id: str) -> TraceResponse:
    result = workflow_service.get_trace(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return result
