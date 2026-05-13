from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:tuyen01233164210@localhost:5432/appdb"
    POSTGRES_PASSWORD: Optional[str] = None  # Docker-only, not used by app

    # Email Configuration (Phase 1: BackgroundTasks)
    SMTP_HOST: str = "smtp.gmail.com"  # or your SMTP provider
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Your email address
    SMTP_PASSWORD: str = ""  # App-specific password (for Gmail, use 2FA app password)
    SMTP_FROM_EMAIL: str = "noreply@fastapi-practice.com"

    # Email Dispatcher (Phase 2: Celery migration)
    # Options: "background_tasks" (Phase 1) or "celery" (Phase 2)
    EMAIL_DISPATCHER: str = "celery"

    # Redis & Celery Configuration (Phase 2)
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Test Mode (Development only)
    # When TEST_MODE=True:
    #   - Test endpoints (/test/*) are ENABLED
    #   - Celery tasks run EAGERLY (synchronously, no Redis needed)
    #   - Ideal for learning/testing Celery logic locally
    # When TEST_MODE=False:
    #   - Test endpoints are DISABLED
    #   - Celery connects to Redis (production-like async)
    #   - Need to run: Redis server + Celery worker
    TEST_MODE: bool = False
    FAKE_EMAIL_FAILURE: bool = False
    FAKE_FAILURE_RATE: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra fields from .env
    )


settings = Settings()
