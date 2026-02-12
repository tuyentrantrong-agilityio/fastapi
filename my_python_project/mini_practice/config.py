from datetime import timedelta
from typing import Optional

class Settings:
    SECRET_KEY = "your-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    APP_NAME = "Task Management API"
    VERSION = "1.0.0"


settings = Settings()
