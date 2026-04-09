from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Core
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:tuyen01233164210@localhost:5432/appdb"
    )

    # Email Configuration (Phase 1: BackgroundTasks)
    SMTP_HOST: str = "smtp.gmail.com"  # or your SMTP provider
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Your email address
    SMTP_PASSWORD: str = ""  # App-specific password (for Gmail, use 2FA app password)
    SMTP_FROM_EMAIL: str = "noreply@fastapi-practice.com"

    # Email Dispatcher (Phase 2: Celery migration)
    # Options: "background_tasks" (Phase 1) or "celery" (Phase 2)
    EMAIL_DISPATCHER: str = "background_tasks"

    # Redis (Phase 2: Celery + Redis)
    # Format: redis://user:password@host:port/db
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
