from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    trace_enabled: bool = True
    auth_required: bool = True
    auth_provider: str = "bearer_claims"
    auth_idp_issuer: str = ""
    auth_idp_audience: str = ""
    auth_claim_user_id_key: str = "sub"
    auth_claim_repo_scopes_key: str = "repos"
    auth_claim_roles_key: str = "roles"
    default_response_language: str = "ko"
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    workspace_root: Path = Path(".")
    store_path: Path = Path(".runtime/workflows.sqlite3")
    trace_export_dir: Path = Path(".runtime/traces")
    repo_connector_provider: str = "workspace"
    docs_connector_provider: str = "workspace"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
