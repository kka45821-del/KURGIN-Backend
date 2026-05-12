from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for KURGIN Backend Auth MVP.

    Production values must be supplied through environment variables.
    Do not commit real .env files or secrets to GitHub.
    """

    environment: str = "development"
    database_url: str = "sqlite:///./data/kurgin_auth_mvp.db"

    jwt_secret: str = Field(
        default="change-this-local-dev-secret-32-plus-chars",
        min_length=32,
        description="Local dev fallback only. Replace in production.",
    )
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "kurgin-backend"
    jwt_audience: str = "kurgin-clients"
    access_token_expire_minutes: int = 60

    allowed_origins: str = (
        "https://kurgin-website.vercel.app,"
        "https://cvdrap.ru,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="KURGIN_",
        extra="ignore",
    )

    @field_validator("environment")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        return value.strip().lower()

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.jwt_secret == "change-this-local-dev-secret-32-plus-chars":
        raise RuntimeError("KURGIN_JWT_SECRET must be set in production.")
    return settings


settings = get_settings()
