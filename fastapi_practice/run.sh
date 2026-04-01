#!/bin/bash
# Start the FastAPI application

echo "Starting FastAPI application..."
uv run uvicorn app.main:app --reload
