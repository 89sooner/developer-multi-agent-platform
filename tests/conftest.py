from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import httpx
import pytest

from src.app.core.config import get_settings
from src.app.core.rate_limit import rate_limiter
from src.app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limit() -> Iterator[None]:
    settings = get_settings()
    previous_limit = settings.rate_limit_requests
    previous_window = settings.rate_limit_window_seconds
    rate_limiter.clear()
    yield
    rate_limiter.clear()
    settings.rate_limit_requests = previous_limit
    settings.rate_limit_window_seconds = previous_window


@pytest.fixture()
async def async_client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer sub=alice;repos=developer-multi-agent-platform;roles=developer"}
