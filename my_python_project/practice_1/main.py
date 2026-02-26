from fastapi import FastAPI
from core.config import settings
from routers import user

app = FastAPI(
    title="Practice 1 API",
    description="FastAPI practice project with structure",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Include routers
app.include_router(user.router)


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
