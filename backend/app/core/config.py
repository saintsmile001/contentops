import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime settings. Secrets are server-only and never returned by routes."""

    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    ai_mock_mode: bool = False
    max_source_size_mb: int = Field(default=10, ge=1, le=100)
    max_source_words: int = Field(default=10_000, ge=100, le=100_000)
    min_source_words: int = Field(default=50, ge=1, le=1_000)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)


@lru_cache
def get_settings() -> Settings:
    """Load only known environment variables, keeping secrets out of responses."""
    env_file = Path(__file__).resolve().parents[2] / ".env"
    file_values: dict[str, str] = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                file_values[key.strip()] = value.strip().strip('"').strip("'")
    fields = {
        "app_env": "APP_ENV",
        "cors_origins": "CORS_ORIGINS",
        "supabase_url": "SUPABASE_URL",
        "supabase_anon_key": "SUPABASE_ANON_KEY",
        "supabase_service_role_key": "SUPABASE_SERVICE_ROLE_KEY",
        "openai_api_key": "OPENAI_API_KEY",
        "openai_model": "OPENAI_MODEL",
        "ai_mock_mode": "AI_MOCK_MODE",
        "max_source_size_mb": "MAX_SOURCE_SIZE_MB",
        "max_source_words": "MAX_SOURCE_WORDS",
        "min_source_words": "MIN_SOURCE_WORDS",
    }
    values = {field: os.environ.get(name, file_values.get(name)) for field, name in fields.items() if os.environ.get(name, file_values.get(name)) is not None}
    return Settings(**values)
