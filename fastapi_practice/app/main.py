from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from .core.config import settings
from .core.handlers import register_exception_handlers
from .db.init_db import create_db_and_tables
from .routers import user, task, project

# ============ Configure logging (optimized) ============
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Silence overly verbose loggers
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("asyncpg").setLevel(logging.WARNING)
logging.getLogger("celery.utils").setLevel(logging.WARNING)  # Suppress Celery internal logs
logging.getLogger("celery.app.trace").setLevel(logging.WARNING)  # Suppress trace logs
logging.getLogger("kombu").setLevel(logging.ERROR)  # Suppress kombu connection warnings
logging.getLogger("asyncio").setLevel(logging.WARNING)  # Suppress asyncio selector logs

# ============ NEW: Import Celery app (must be before creating FastAPI app) ============
from .tasks.celery_app import celery_app  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    await create_db_and_tables()
    print("Database tables created successfully!")
    yield


app = FastAPI(
    title="FastAPI Practice API",
    description="FastAPI practice project with structure",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Register global exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(user.router)
app.include_router(task.router)
app.include_router(project.router)

# ============ NEW: Include test routes (only when TEST_MODE=True) ============
if settings.TEST_MODE:
    from .api.test_routes import router as test_router
    app.include_router(test_router)
    print("[STARTUP] Test routes registered (TEST_MODE=True)")


@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI Practice API",
        "debug": settings.DEBUG,
        "test_mode": settings.TEST_MODE,
        "docs": "/docs",
        "celery_status": "Check /test/status (if TEST_MODE=True)"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
