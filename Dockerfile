# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Optimize Docker layer caching by separating dependencies
# Copy only pyproject.toml and README.md first
COPY pyproject.toml README.md ./

# Create a dummy app directory so setuptools doesn't fail building the wheel
RUN mkdir app && touch app/__init__.py

# Install dependencies using pip
RUN pip install .

# Now copy the actual application code
COPY . .

# Expose the port Uvicorn runs on
EXPOSE 8000

# Command to run the FastAPI application
# Railway sets PORT env var automatically, fallback to 8000 for local development
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
