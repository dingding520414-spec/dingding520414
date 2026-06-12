from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration."""

    APP_NAME: str = "SeniorStrength API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-abc123xyz789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for dev
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database (SQLite - no external server needed)
    DATABASE_URL: str = "sqlite+aiosqlite:///data/seniorstrength.db"
    SYNC_DATABASE_URL: str = "sqlite:///data/seniorstrength.db"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Rate limiting (skip in dev)
    RATE_LIMIT_PER_MINUTE: int = 9999
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 9999

    # Stripe (optional - will work without real keys)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()