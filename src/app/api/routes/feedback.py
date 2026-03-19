from fastapi import APIRouter, Depends, HTTPException

from src.app.contracts.requests import FeedbackRequest
from src.app.contracts.responses import FeedbackResponse
from src.app.core.auth import UserContext, get_user_context
from src.app.services.workflow_service import workflow_service

router = APIRouter()


@router.post("", response_model=FeedbackResponse)
async def create_feedback(request: FeedbackRequest, user: UserContext = Depends(get_user_context)) -> FeedbackResponse:
    try:
        return workflow_service.create_feedback(request, user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
