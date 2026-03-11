#!/bin/bash
# Start the FastAPI application

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Please run: source ../venv/Scripts/activate"
    exit 1
fi

echo "Starting FastAPI application..."
python main.py
