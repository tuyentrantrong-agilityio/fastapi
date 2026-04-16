from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.handlers import register_exception_handlers
from .core.logging_config import setup_json_logging
from .db.init_db import create_db_and_tables
from .routers import user, task, project, websocket
from .middleware.logging_middleware import LoggingMiddleware
from .tasks.celery_app import celery_app

# Setup logging FIRST
setup_json_logging(use_json=settings.DEBUG is False)

logger = logging.getLogger(__name__)
logger.info("FastAPI application initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    await create_db_and_tables()
    logger.info("Database tables created successfully!")
    yield


app = FastAPI(
    title="FastAPI Practice API",
    description="FastAPI practice project with structure",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# ============ Logging Middleware (MUST BE FIRST) ============
app.add_middleware(LoggingMiddleware)

# ============ CORS Configuration ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(user.router)
app.include_router(task.router)
app.include_router(project.router)
app.include_router(websocket.router)

# ============ Include internal integration test routes (only when TEST_MODE=True) ============
if settings.TEST_MODE:
    from .api.test_routes import router as internal_router

    app.include_router(internal_router)
    logger.info(
        "[STARTUP]  Internal integration test routes registered (TEST_MODE=True)"
    )


@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI Practice API",
        "debug": settings.DEBUG,
        "environment": "Development (TEST_MODE=True)"
        if settings.TEST_MODE
        else "Production (TEST_MODE=False)",
        "docs": "/docs",
        "internal_tools": "Available at /internal/* (Dev/Staging only)"
        if settings.TEST_MODE
        else "Disabled",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
