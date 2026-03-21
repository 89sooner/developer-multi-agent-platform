from __future__ import annotations

import pytest

from src.app.core.auth import AUTH_PROVIDERS, UserContext
from src.app.core.config import get_settings


class StaticAuthProvider:
    def build_context(self, raw_token: str, *, request_id: str, language: str) -> UserContext:
        return UserContext(
            user_id="stub-user",
            repo_scopes=["developer-multi-agent-platform"],
            roles=["developer"],
            request_id=request_id,
            language=language,
        )


@pytest.mark.anyio
async def test_default_auth_provider_uses_bearer_claims(async_client) -> None:
    settings = get_settings()
    previous_provider = settings.auth_provider
    settings.auth_provider = "bearer_claims"
    try:
        response = await async_client.post(
            "/v1/workflows/plan",
            headers={"Authorization": "Bearer sub=alice;repos=developer-multi-agent-platform;roles=developer"},
            json={
                "repo_id": "developer-multi-agent-platform",
                "branch": "main",
                "task_text": "auth provider default behavior check",
            },
        )
        assert response.status_code == 200
        run_id = response.json()["run_id"]

        run_response = await async_client.get(
            f"/v1/workflows/{run_id}",
            headers={"Authorization": "Bearer sub=alice;repos=developer-multi-agent-platform;roles=developer"},
        )
        assert run_response.status_code == 200
        assert run_response.json()["user_id"] == "alice"
    finally:
        settings.auth_provider = previous_provider


@pytest.mark.anyio
async def test_auth_provider_can_be_selected_from_config(async_client) -> None:
    settings = get_settings()
    previous_provider = settings.auth_provider
    AUTH_PROVIDERS["test_static"] = StaticAuthProvider()
    settings.auth_provider = "test_static"
    try:
        response = await async_client.post(
            "/v1/workflows/plan",
            headers={"Authorization": "Bearer ignored-by-static-provider"},
            json={
                "repo_id": "developer-multi-agent-platform",
                "branch": "main",
                "task_text": "auth provider selection check",
            },
        )
        assert response.status_code == 200
        run_id = response.json()["run_id"]

        run_response = await async_client.get(
            f"/v1/workflows/{run_id}",
            headers={"Authorization": "Bearer ignored-by-static-provider"},
        )
        assert run_response.status_code == 200
        assert run_response.json()["user_id"] == "stub-user"
    finally:
        settings.auth_provider = previous_provider
        AUTH_PROVIDERS.pop("test_static", None)
