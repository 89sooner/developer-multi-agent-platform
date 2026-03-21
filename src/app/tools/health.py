from __future__ import annotations

from pathlib import Path

from src.app.contracts.responses import ConnectorHealth, HealthResponse
from src.app.core.config import get_settings
from src.app.tools.connectors import ConnectorConfigurationError, get_connector_registry

ROOT = Path(__file__).resolve().parents[3]


def get_health_response(*, version: str) -> HealthResponse:
    settings = get_settings()
    registry = get_connector_registry()
    connectors = {
        "repo": _selected_connector_health(
            connector_type="repo",
            provider_name=settings.repo_connector_provider,
            resolver=registry.get_repo_connector,
        ),
        "docs": _selected_connector_health(
            connector_type="docs",
            provider_name=settings.docs_connector_provider,
            resolver=registry.get_docs_connector,
        ),
        "issue": _optional_dir_health(
            [ROOT / "data" / "issues", ROOT / ".runtime" / "issues"],
            "issue source directories",
        ),
        "ci": _optional_dir_health(
            [ROOT / "data" / "ci", ROOT / ".runtime" / "ci"],
            "ci source directories",
        ),
    }
    overall = "ok" if all(item.status == "ok" for item in connectors.values()) else "degraded"
    return HealthResponse(status=overall, version=version, connectors=connectors)


def _dir_health(path: Path, detail: str) -> ConnectorHealth:
    if path.exists():
        return ConnectorHealth(status="ok", detail=detail)
    return ConnectorHealth(status="degraded", detail=f"missing {detail}")


def _optional_dir_health(paths: list[Path], detail: str) -> ConnectorHealth:
    if any(path.exists() for path in paths):
        return ConnectorHealth(status="ok", detail=detail)
    return ConnectorHealth(status="unconfigured", detail=f"no configured {detail}")


def _selected_connector_health(connector_type: str, provider_name: str, resolver) -> ConnectorHealth:
    try:
        connector = resolver(provider_name)
    except ConnectorConfigurationError as exc:
        return ConnectorHealth(
            status="degraded",
            detail=str(exc),
        )
    return connector.health()
