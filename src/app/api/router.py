from fastapi import APIRouter

from src.app.api.routes import feedback, workflows

api_router = APIRouter()
api_router.include_router(workflows.router, prefix="/v1/workflows", tags=["workflows"])
api_router.include_router(feedback.router, prefix="/v1/feedback", tags=["feedback"])
