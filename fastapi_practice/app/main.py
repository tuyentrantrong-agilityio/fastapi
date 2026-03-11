from fastapi import FastAPI
from .core.config import settings
from .core.handlers import register_exception_handlers
from .routers import user, task, project

app = FastAPI(
    title="Practice 1 API",
    description="FastAPI practice project with structure",
    version="1.0.0",
    debug=settings.DEBUG,
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
        "message": "Welcome to Practice 1 API",
        "debug": settings.DEBUG,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
