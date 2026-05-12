from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Values must come from environment variables in production."""

    environment: str = "development"
    database_url: str = "postgresql+psycopg://user:password@localhost:5432/kurgin"
    jwt_issuer: str = "kurgin-api"
    jwt_audience: str = "kurgin-clients"
    jwt_secret: str = "CHANGE_ME_IN_ENV_ONLY"
    allowed_origins: str = "https://kurgin-website.vercel.app,https://cvdrap.ru,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
