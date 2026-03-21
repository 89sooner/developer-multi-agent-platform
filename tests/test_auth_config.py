from __future__ import annotations

from src.app.core.config import get_settings


def test_auth_claim_mapping_defaults_match_local_bearer_claims_provider() -> None:
    settings = get_settings()

    assert settings.auth_provider == "bearer_claims"
    assert settings.auth_claim_user_id_key == "sub"
    assert settings.auth_claim_repo_scopes_key == "repos"
    assert settings.auth_claim_roles_key == "roles"


def test_auth_claim_mapping_settings_are_mutable_for_future_idp_wiring() -> None:
    settings = get_settings()
    previous_values = (
        settings.auth_idp_issuer,
        settings.auth_idp_audience,
        settings.auth_claim_user_id_key,
        settings.auth_claim_repo_scopes_key,
        settings.auth_claim_roles_key,
    )

    try:
        settings.auth_idp_issuer = "https://idp.example.internal"
        settings.auth_idp_audience = "developer-multi-agent-platform"
        settings.auth_claim_user_id_key = "preferred_username"
        settings.auth_claim_repo_scopes_key = "repositories"
        settings.auth_claim_roles_key = "groups"

        assert settings.auth_idp_issuer == "https://idp.example.internal"
        assert settings.auth_idp_audience == "developer-multi-agent-platform"
        assert settings.auth_claim_user_id_key == "preferred_username"
        assert settings.auth_claim_repo_scopes_key == "repositories"
        assert settings.auth_claim_roles_key == "groups"
    finally:
        (
            settings.auth_idp_issuer,
            settings.auth_idp_audience,
            settings.auth_claim_user_id_key,
            settings.auth_claim_repo_scopes_key,
            settings.auth_claim_roles_key,
        ) = previous_values
