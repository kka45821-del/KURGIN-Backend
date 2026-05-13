from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for KURGIN Backend Auth + Workspace Hardening V1.

    Production values must be provided only through environment variables or
    deployment secret managers. Do not commit real secrets to GitHub.
    """

    environment: str = "development"
    app_name: str = "KURGIN Backend API"
    api_version: str = "1.1.0-auth-hardening"

    # Local SQLite remains MVP/private preview storage. PostgreSQL is the production target.
    database_url: str = "sqlite:///./data/kurgin_auth_mvp.sqlite3"

    jwt_secret: str = Field(
        default="change-this-local-dev-secret-32-plus-chars",
        min_length=32,
        description="Local dev fallback only. Replace in production.",
    )
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "kurgin-api"
    jwt_audience: str = "kurgin-clients"
    access_token_expire_minutes: int = 60

    # Refresh-token MVP. HttpOnly refresh cookie is enabled when /auth/login or /auth/register succeeds.
    refresh_token_cookie_name: str = "kurgin_refresh_token"
    refresh_token_expire_days: int = 14
    refresh_cookie_secure: bool = True
    refresh_cookie_samesite: str = "none"

    allowed_origins: str = (
        "https://kurgin-website.vercel.app,"
        "https://cvdrap.ru,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://127.0.0.1:8000"
    )

    # Must remain false in production. Professional access is granted through role requests/admin approval.
    allow_self_assign_professional_roles: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="KURGIN_",
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() in {"production", "prod"}

    @property
    def is_default_secret(self) -> bool:
        return self.jwt_secret == "change-this-local-dev-secret-32-plus-chars"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.is_default_secret:
        raise RuntimeError("KURGIN_JWT_SECRET must be set in production.")
    return settings


settings = get_settings()
