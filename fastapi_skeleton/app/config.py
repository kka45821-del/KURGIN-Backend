from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for local Auth MVP.

    Production values must be provided only through environment variables or
    the deployment secret manager. Do not commit real secrets to GitHub.
    """

    environment: str = "development"
    app_name: str = "KURGIN Backend API"
    api_version: str = "1.0.0-auth-mvp"

    # Local SQLite is for MVP/dev only. Production target remains PostgreSQL.
    local_db_path: str = ".local/kurgin_auth_mvp.sqlite"
    database_url: str = "postgresql+psycopg://user:password@localhost:5432/kurgin"

    jwt_secret: str = "CHANGE_ME_FOR_LOCAL_DEV_ONLY"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "kurgin-api"
    jwt_audience: str = "kurgin-clients"
    access_token_expire_minutes: int = 60

    allowed_origins: str = "https://kurgin-website.vercel.app,https://cvdrap.ru,http://localhost:3000,http://127.0.0.1:3000"

    # Default false prevents users from granting themselves professional roles.
    allow_self_assign_professional_roles: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_default_secret(self) -> bool:
        return self.jwt_secret == "CHANGE_ME_FOR_LOCAL_DEV_ONLY"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
