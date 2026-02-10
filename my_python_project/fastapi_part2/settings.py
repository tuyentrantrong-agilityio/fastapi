# main.py
from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "My API"
    debug: bool = False
    admin_email: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


app = FastAPI()


@app.get("/info")
def info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "admin_email": settings.admin_email,
    }
