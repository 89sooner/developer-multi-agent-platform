from __future__ import annotations

import re

from fastapi import HTTPException, status

from src.app.contracts.responses import ConfidenceLevel, Evidence
from src.app.core.auth import UserContext

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{6,})"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{10,}"),
]


def mask_sensitive_text(text: str | None) -> str | None:
    if text is None:
        return None
    masked = text
    for pattern in SECRET_PATTERNS:
        masked = pattern.sub(lambda match: match.group(0).split(match.group(2))[0] + "[REDACTED]" if match.lastindex and match.lastindex >= 2 else "[REDACTED]", masked)
    return masked


def mask_evidence(evidence: list[Evidence]) -> list[Evidence]:
    masked: list[Evidence] = []
    for item in evidence:
        masked.append(item.model_copy(update={"snippet": mask_sensitive_text(item.snippet)}))
    return masked


def enforce_repo_scope(user: UserContext, repo_id: str) -> None:
    if "*" in user.repo_scopes or repo_id in user.repo_scopes:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"repo scope violation for repo_id={repo_id}",
    )


def require_approval(write_actions: list[str], approval_token: str | None) -> None:
    if not write_actions:
        return
    if approval_token is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="approval token required for write actions",
        )

    approved = {item.strip() for item in approval_token.replace("approve:", "").split(",") if item.strip()}
    if "*" in approved:
        return
    if not set(write_actions).issubset(approved):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="approval token does not cover requested write actions",
        )


def confidence_from_counts(*, evidence_count: int, uncertainty_count: int) -> ConfidenceLevel:
    if evidence_count == 0:
        return "low"
    if evidence_count >= 4 and uncertainty_count <= 1:
        return "high"
    return "medium"
