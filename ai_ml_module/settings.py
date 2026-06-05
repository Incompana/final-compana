"""Runtime settings for the FastAPI demo service."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str
    cors_origins: list[str]
    gemini_api_key: str
    compana_ai_provider: str

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


def get_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "development")
    default_origins = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5500,http://localhost:8000"
    cors_origins = _split_csv(os.getenv("CORS_ORIGINS", default_origins))

    if app_env.lower() == "production" and "*" in cors_origins:
        raise RuntimeError("CORS_ORIGINS must not contain '*' when APP_ENV=production")

    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("COMPANA_AI_API_KEY", "")
    compana_ai_provider = os.getenv("COMPANA_AI_PROVIDER", "gemini")

    return Settings(
        app_env=app_env,
        cors_origins=cors_origins,
        gemini_api_key=gemini_api_key,
        compana_ai_provider=compana_ai_provider,
    )
