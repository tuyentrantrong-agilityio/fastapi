@echo off
REM FastAPI Project Setup Script for Windows

echo.
echo ========================================
echo FastAPI Project Setup
echo ========================================
echo.

REM Step 1: Create Virtual Environment
echo [1/4] Creating virtual environment (.venv)...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created

REM Step 2: Activate Virtual Environment
echo.
echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Step 3: Install Dependencies
echo.
echo [3/4] Installing dependencies from pyproject.toml...
pip install -e ".[dev]"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Step 4: Setup Environment File
echo.
echo [4/4] Setting up environment file...
if exist .env (
    echo [SKIP] .env already exists
) else (
    if exist .env.example (
        copy .env.example .env > nul
        echo [OK] .env created from .env.example
    ) else (
        echo [WARN] .env.example not found, skipping .env setup
    )
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate virtual environment (if not already):
echo    .venv\Scripts\activate
echo.
echo 2. Run the application:
echo    uvicorn app.main:app --reload
echo.
echo 3. Run tests:
echo    pytest tests/ -v
echo.
