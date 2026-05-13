@echo off
REM Start the FastAPI application on Windows

echo Starting FastAPI application...
uv run uvicorn app.main:app --reload
