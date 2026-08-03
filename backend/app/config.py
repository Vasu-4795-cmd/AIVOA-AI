"""
Centralized application settings, loaded from environment variables / .env.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    groq_api_key: str = ""
    groq_extraction_model: str = "gemma2-9b-it"
    groq_context_model: str = "llama-3.3-70b-versatile"

    # Database
    database_url: str = "sqlite:///./aivoa_dev.db"  # safe local default

    # App
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Managed Postgres providers (Render, Heroku, etc.) hand out URLs that start
        with 'postgres://' or plain 'postgresql://'. SQLAlchemy needs the explicit
        psycopg2 driver in the scheme, so normalize it here instead of requiring
        every deploy target to know that detail.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    @property
    def groq_enabled(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
