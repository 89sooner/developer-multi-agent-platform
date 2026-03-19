from fastapi import APIRouter, Depends, HTTPException

from src.app.contracts.requests import PlanRequest, ReviewRequest, TestPlanRequest
from src.app.contracts.responses import (
    PlanResponse,
    ReviewResponse,
    RunDetailResponse,
    TestPlanResponse,
    TraceResponse,
)
from src.app.core.auth import UserContext, get_user_context
from src.app.services.workflow_service import workflow_service

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest, user: UserContext = Depends(get_user_context)) -> PlanResponse:
    return workflow_service.create_plan(request, user)


@router.post("/review", response_model=ReviewResponse)
async def create_review(request: ReviewRequest, user: UserContext = Depends(get_user_context)) -> ReviewResponse:
    return workflow_service.create_review(request, user)


@router.post("/test-plan", response_model=TestPlanResponse)
async def create_test_plan(request: TestPlanRequest, user: UserContext = Depends(get_user_context)) -> TestPlanResponse:
    return workflow_service.create_test_plan(request, user)


@router.get("/{run_id}", response_model=RunDetailResponse)
async def get_run(run_id: str, user: UserContext = Depends(get_user_context)) -> RunDetailResponse:
    try:
        result = workflow_service.get_run(run_id, user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="run not found")
    return result


@router.get("/{run_id}/trace", response_model=TraceResponse)
async def get_trace(run_id: str, user: UserContext = Depends(get_user_context)) -> TraceResponse:
    try:
        result = workflow_service.get_trace(run_id, user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return result
