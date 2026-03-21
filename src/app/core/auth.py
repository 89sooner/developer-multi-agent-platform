from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from fastapi import Header, HTTPException, Request, status

from src.app.core.config import get_settings
from src.app.core.rate_limit import rate_limiter


@dataclass(slots=True)
class UserContext:
    user_id: str
    repo_scopes: list[str]
    roles: list[str]
    request_id: str
    language: str


class AuthProvider(Protocol):
    def build_context(self, raw_token: str, *, request_id: str, language: str) -> UserContext:
        ...


def _parse_claims(raw_token: str) -> dict[str, str]:
    claims: dict[str, str] = {}
    for part in raw_token.split(";"):
        key, sep, value = part.partition("=")
        if not sep:
            key, sep, value = part.partition(":")
        if sep and key:
            claims[key.strip()] = value.strip()
    return claims


def _build_context(raw_token: str, request_id: str, language: str) -> UserContext:
    claims = _parse_claims(raw_token)
    user_id = claims.get("sub") or claims.get("user") or claims.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid bearer token: missing user claim",
        )

    repo_scopes = [value for value in claims.get("repos", "").split(",") if value]
    roles = [value for value in claims.get("roles", "developer").split(",") if value]
    return UserContext(
        user_id=user_id,
        repo_scopes=repo_scopes or ["*"],
        roles=roles or ["developer"],
        request_id=request_id,
        language=language,
    )


@dataclass(slots=True)
class BearerClaimsAuthProvider:
    def build_context(self, raw_token: str, *, request_id: str, language: str) -> UserContext:
        return _build_context(raw_token, request_id=request_id, language=language)


AUTH_PROVIDERS: dict[str, AuthProvider] = {
    "bearer_claims": BearerClaimsAuthProvider(),
}


def get_auth_provider(provider_name: str) -> AuthProvider:
    provider = AUTH_PROVIDERS.get(provider_name)
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unsupported auth provider: {provider_name}",
        )
    return provider


async def get_user_context(
    request: Request,
    authorization: str | None = Header(default=None),
    x_request_id: str | None = Header(default=None),
    x_user_language: str | None = Header(default=None),
) -> UserContext:
    settings = get_settings()
    request_id = getattr(request.state, "request_id", None) or x_request_id or f"req_{uuid4().hex[:8]}"
    language = x_user_language or settings.default_response_language

    if not settings.auth_required:
        context = UserContext(
            user_id="local-user",
            repo_scopes=["*"],
            roles=["developer"],
            request_id=request_id,
            language=language,
        )
        request.state.user_context = context
        return context

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
        )

    raw_token = authorization.removeprefix("Bearer ").strip()
    provider = get_auth_provider(settings.auth_provider)
    context = provider.build_context(raw_token, request_id=request_id, language=language)
    rate_limiter.check(context.user_id)
    request.state.user_context = context
    return context
