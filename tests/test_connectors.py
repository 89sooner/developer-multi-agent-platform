from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.app.agents.repo_context import run_repo_context_agent
from src.app.contracts.requests import ArtifactRefs, BaseWorkflowRequest
from src.app.contracts.responses import ConnectorHealth, Evidence
from src.app.core.config import get_settings
from src.app.tools.connectors import (
    ConnectorAuthError,
    ConnectorConfigurationError,
    ConnectorEmptyResultError,
    ConnectorRegistry,
    ConnectorTimeoutError,
    WorkspaceDocsConnector,
    WorkspaceRepoConnector,
    get_connector_registry,
    set_connector_registry,
)


class StubRepoConnector:
    name = "stub"

    def search_repo(self, repo_id: str, branch: str, query: str, *, changed_files: list[str] | None = None) -> list[Evidence]:
        _ = (repo_id, branch, query, changed_files)
        return [
            Evidence(
                source_type="repo",
                locator="src/app/stub_repo.py",
                snippet="stub repo evidence",
                confidence="high",
            )
        ]

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(status="ok", detail="stub repo connector")


class StubDocsConnector:
    name = "stub"

    def search_docs(self, repo_id: str, query: str) -> list[Evidence]:
        _ = (repo_id, query)
        return [
            Evidence(
                source_type="docs",
                locator="docs/stub.md",
                snippet="stub docs evidence",
                confidence="high",
            )
        ]

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(status="ok", detail="stub docs connector")


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "connector_error_cases.json"


def test_workspace_connector_registry_defaults() -> None:
    registry = ConnectorRegistry(
        repo_connectors={"workspace": WorkspaceRepoConnector()},
        docs_connectors={"workspace": WorkspaceDocsConnector()},
    )

    repo_connector = registry.get_repo_connector("workspace")
    docs_connector = registry.get_docs_connector("workspace")

    repo_results = repo_connector.search_repo(
        "developer-multi-agent-platform",
        "main",
        "workflow_service",
        changed_files=["src/app/services/workflow_service.py"],
    )
    docs_results = docs_connector.search_docs("developer-multi-agent-platform", "phase")

    assert repo_connector.health().status == "ok"
    assert docs_connector.health().status == "ok"
    assert repo_results
    assert docs_results
    assert all(item.source_type == "repo" for item in repo_results)
    assert all(item.source_type == "docs" for item in docs_results)


def test_repo_context_uses_selected_registry_connectors() -> None:
    settings = get_settings()
    previous_repo_provider = settings.repo_connector_provider
    previous_docs_provider = settings.docs_connector_provider
    previous_registry = get_connector_registry()

    custom_registry = ConnectorRegistry(
        repo_connectors={"stub": StubRepoConnector()},
        docs_connectors={"stub": StubDocsConnector()},
    )

    settings.repo_connector_provider = "stub"
    settings.docs_connector_provider = "stub"
    set_connector_registry(custom_registry)
    try:
        request = BaseWorkflowRequest(
            repo_id="developer-multi-agent-platform",
            branch="main",
            task_text="connector selection",
            artifacts=ArtifactRefs(issue_ids=[], changed_files=[]),
        )
        result = run_repo_context_agent(request)

        assert "src/app/stub_repo.py" in result.related_files
        assert "docs/stub.md" in result.relevant_docs
        assert any(item.source_type == "repo" for item in result.evidence)
        assert any(item.source_type == "docs" for item in result.evidence)
    finally:
        settings.repo_connector_provider = previous_repo_provider
        settings.docs_connector_provider = previous_docs_provider
        set_connector_registry(previous_registry)


def test_missing_provider_raises_typed_configuration_error() -> None:
    registry = ConnectorRegistry()

    with pytest.raises(ConnectorConfigurationError) as exc_info:
        registry.get_repo_connector("missing")

    assert exc_info.value.kind == "configuration"
    assert exc_info.value.connector_type == "repo"
    assert exc_info.value.provider_name == "missing"


def test_connector_error_fixture_contract_examples() -> None:
    cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    error_classes = {
        "configuration": ConnectorConfigurationError,
        "auth": ConnectorAuthError,
        "timeout": ConnectorTimeoutError,
        "empty_result": ConnectorEmptyResultError,
    }

    for case in cases:
        error = error_classes[case["kind"]](
            connector_type=case["connector_type"],
            provider_name=case["provider_name"],
            kind=case["kind"],
            detail=case["detail"],
        )
        assert error.connector_type == case["connector_type"]
        assert error.provider_name == case["provider_name"]
        assert error.kind == case["kind"]
        assert str(error) == case["detail"]
