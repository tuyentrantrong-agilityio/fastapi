from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.config import settings
from .core.handlers import register_exception_handlers
from .db.init_db import create_db_and_tables
from .routers import user, task, project


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


@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI Practice API",
        "debug": settings.DEBUG,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
