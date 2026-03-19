from fastapi import FastAPI

from src.app.api.router import api_router
from src.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Developer Multi-Agent Workflow API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
