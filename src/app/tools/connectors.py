from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

from src.app.contracts.responses import ConnectorHealth, Evidence


ROOT = Path(__file__).resolve().parents[3]

ConnectorErrorKind = Literal["configuration", "timeout", "auth", "empty_result"]


@dataclass(slots=True)
class ConnectorError(Exception):
    connector_type: str
    provider_name: str
    kind: ConnectorErrorKind
    detail: str

    def __str__(self) -> str:
        return self.detail


class ConnectorConfigurationError(ConnectorError):
    pass


class ConnectorTimeoutError(ConnectorError):
    pass


class ConnectorAuthError(ConnectorError):
    pass


class ConnectorEmptyResultError(ConnectorError):
    pass


class RepoConnector(Protocol):
    name: str

    def search_repo(self, repo_id: str, branch: str, query: str, *, changed_files: list[str] | None = None) -> list[Evidence]:
        ...

    def health(self) -> ConnectorHealth:
        ...


class DocsConnector(Protocol):
    name: str

    def search_docs(self, repo_id: str, query: str) -> list[Evidence]:
        ...

    def health(self) -> ConnectorHealth:
        ...


@dataclass(slots=True)
class WorkspaceRepoConnector:
    name: str = "workspace"
    workspace_root: Path = ROOT

    def search_repo(self, repo_id: str, branch: str, query: str, *, changed_files: list[str] | None = None) -> list[Evidence]:
        from src.app.tools.repo_search import search_repo

        return search_repo(repo_id, branch, query, changed_files=changed_files)

    def health(self) -> ConnectorHealth:
        source_dir = self.workspace_root / "src"
        if source_dir.exists():
            return ConnectorHealth(status="ok", detail="workspace source directory")
        return ConnectorHealth(status="degraded", detail="missing workspace source directory")


@dataclass(slots=True)
class WorkspaceDocsConnector:
    name: str = "workspace"
    workspace_root: Path = ROOT

    def search_docs(self, repo_id: str, query: str) -> list[Evidence]:
        from src.app.tools.docs_search import search_docs

        return search_docs(repo_id, query)

    def health(self) -> ConnectorHealth:
        docs_dir = self.workspace_root / "docs"
        if docs_dir.exists():
            return ConnectorHealth(status="ok", detail="workspace docs directory")
        return ConnectorHealth(status="degraded", detail="missing workspace docs directory")


@dataclass(slots=True)
class ConnectorRegistry:
    repo_connectors: dict[str, RepoConnector] = field(default_factory=dict)
    docs_connectors: dict[str, DocsConnector] = field(default_factory=dict)

    def register_repo_connector(self, provider_name: str, connector: RepoConnector) -> None:
        self.repo_connectors[provider_name] = connector

    def register_docs_connector(self, provider_name: str, connector: DocsConnector) -> None:
        self.docs_connectors[provider_name] = connector

    def get_repo_connector(self, provider_name: str) -> RepoConnector:
        connector = self.repo_connectors.get(provider_name)
        if connector is None:
            raise ConnectorConfigurationError(
                connector_type="repo",
                provider_name=provider_name,
                kind="configuration",
                detail=f"unsupported repo connector provider: {provider_name}",
            )
        return connector

    def get_docs_connector(self, provider_name: str) -> DocsConnector:
        connector = self.docs_connectors.get(provider_name)
        if connector is None:
            raise ConnectorConfigurationError(
                connector_type="docs",
                provider_name=provider_name,
                kind="configuration",
                detail=f"unsupported docs connector provider: {provider_name}",
            )
        return connector


_connector_registry = ConnectorRegistry(
    repo_connectors={"workspace": WorkspaceRepoConnector()},
    docs_connectors={"workspace": WorkspaceDocsConnector()},
)


def get_connector_registry() -> ConnectorRegistry:
    return _connector_registry


def set_connector_registry(registry: ConnectorRegistry) -> None:
    global _connector_registry
    _connector_registry = registry
