from fastapi import APIRouter

from src.app.contracts.requests import FeedbackRequest
from src.app.contracts.responses import FeedbackResponse
from src.app.services.workflow_service import workflow_service

router = APIRouter()


@router.post("", response_model=FeedbackResponse)
def create_feedback(request: FeedbackRequest) -> FeedbackResponse:
    return workflow_service.create_feedback(request)
