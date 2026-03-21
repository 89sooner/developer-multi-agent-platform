import pytest


@pytest.mark.anyio
async def test_health(async_client) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert payload["connectors"]["repo"]["status"] == "ok"
    assert payload["connectors"]["docs"]["status"] == "ok"
