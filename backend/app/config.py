from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ── LLM API Keys ─────────────────────────────────────────────────────
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # LLM Models
    primary_llm: str = "gpt-4o"
    fallback_llm: str = "gpt-4o-mini"

    # Database
    database_url: str = "sqlite:///./ecommerce.db"

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # App metadata
    app_name: str = "Agentic Customer Care"
    app_version: str = "1.0.0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
