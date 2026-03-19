from __future__ import annotations

import pytest

from src.app.core.config import get_settings


@pytest.mark.anyio
async def test_plan_workflow_persists_trace_and_run(async_client, auth_headers) -> None:
    response = await async_client.post(
        "/v1/workflows/plan",
        headers=auth_headers,
        json={
            "repo_id": "developer-multi-agent-platform",
            "branch": "main",
            "task_text": "workflow service 에 SQLite 기반 persistent run store 와 trace export 를 추가해줘.",
            "artifacts": {"issue_ids": [], "changed_files": []},
            "options": {"include_tests": True, "language": "ko"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["primary_intent"] in {"feature", "refactor"}
    assert "workflow-orchestrator" in payload["selected_agents"]
    assert "requirements-planner" in payload["selected_agents"]
    assert "review-gate" in payload["selected_agents"]
    assert payload["model_version"] == get_settings().openai_model
    assert payload["skill_versions"]["summary-composer"] == "builtin-v1"
    assert payload["evidence"]

    run_id = payload["run_id"]
    run_response = await async_client.get(f"/v1/workflows/{run_id}", headers=auth_headers)
    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["user_id"] == "alice"
    assert "developer-multi-agent-platform" in run_payload["repo_scope"]

    trace_response = await async_client.get(f"/v1/workflows/{run_id}/trace", headers=auth_headers)
    assert trace_response.status_code == 200
    trace_payload = trace_response.json()
    assert [step["step_name"] for step in trace_payload["steps"]][-2:] == ["review", "summary"]
    assert trace_payload["tool_calls"]
    assert trace_payload["exported_at"] is not None


@pytest.mark.anyio
async def test_scope_violation_is_rejected(async_client) -> None:
    response = await async_client.post(
        "/v1/workflows/plan",
        headers={"Authorization": "Bearer sub=bob;repos=other-repo;roles=developer"},
        json={
            "repo_id": "developer-multi-agent-platform",
            "branch": "main",
            "task_text": "api 변경 영향 범위를 확인해줘",
        },
    )

    assert response.status_code == 403
    assert "scope violation" in response.json()["detail"]


@pytest.mark.anyio
async def test_approval_gate_blocks_unapproved_write_actions(async_client, auth_headers) -> None:
    response = await async_client.post(
        "/v1/workflows/plan",
        headers=auth_headers,
        json={
            "repo_id": "developer-multi-agent-platform",
            "branch": "main",
            "task_text": "create pr 까지 해줘",
            "options": {
                "include_tests": True,
                "language": "ko",
                "write_actions": ["create_pr"],
            },
        },
    )

    assert response.status_code == 409
    assert "approval token required" in response.json()["detail"]


@pytest.mark.anyio
async def test_review_workflow_runs_with_changed_files(async_client, auth_headers) -> None:
    response = await async_client.post(
        "/v1/workflows/review",
        headers=auth_headers,
        json={
            "repo_id": "developer-multi-agent-platform",
            "branch": "main",
            "task_text": "이 PR 초안의 리스크와 누락 테스트를 review 해줘",
            "artifacts": {"changed_files": ["src/app/services/workflow_service.py"]},
            "options": {"include_tests": True, "language": "ko"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["primary_intent"] == "review"
    assert "review-gate" in payload["selected_agents"]
    assert payload["readiness_verdict"] in {"ready", "needs_changes", "blocked"}


@pytest.mark.anyio
async def test_rate_limit_returns_429(async_client, auth_headers) -> None:
    settings = get_settings()
    settings.rate_limit_requests = 1
    settings.rate_limit_window_seconds = 60

    first = await async_client.post(
        "/v1/workflows/plan",
        headers=auth_headers,
        json={
            "repo_id": "developer-multi-agent-platform",
            "branch": "main",
            "task_text": "첫 번째 요청",
        },
    )
    second = await async_client.post(
        "/v1/workflows/plan",
        headers=auth_headers,
        json={
            "repo_id": "developer-multi-agent-platform",
            "branch": "main",
            "task_text": "두 번째 요청",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 429
