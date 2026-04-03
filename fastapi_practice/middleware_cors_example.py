"""
Middleware & CORS Example

Usage:
  python middleware_cors_example.py
"""

import time
from datetime import datetime
from typing import Callable
from uuid import uuid4

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager


class LoginRequest(BaseModel):
    username: str
    password: str


async def log_requests_middleware(request: Request, call_next: Callable):
    """Log all requests and responses"""
    request_id = str(uuid4())[:8]
    method = request.method
    path = request.url.path
    client_ip = request.client.host if request.client else "unknown"

    start_time = time.time()
    print(f"\n[REQUEST] {method} {path} from {client_ip} (ID: {request_id})")

    try:
        response = await call_next(request)
    except Exception as exc:
        print(f"[REQUEST] ✗ Error: {str(exc)}")
        response = JSONResponse(status_code=500, content={"error": "Internal error"})

    process_time = time.time() - start_time
    print(f"[RESPONSE] {response.status_code} in {process_time:.3f}s\n")

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    return response


async def auth_middleware(request: Request, call_next: Callable):
    """Check auth for protected routes"""
    protected_routes = ["/protected", "/admin"]
    path = request.url.path

    is_protected = any(path.startswith(route) for route in protected_routes)

    if is_protected:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            print(f"[AUTH] ✗ Missing token for {path}")
            return JSONResponse(
                status_code=401, content={"detail": "Missing Authorization header"}
            )

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError()
            print(f"[AUTH] ✓ Valid token for {path}")
        except:
            print(f"[AUTH] ✗ Invalid token format")
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    return await call_next(request)


# ============================================================================
# FASTAPI APP WITH MIDDLEWARE & CORS
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    print("\n" + "=" * 60)
    print("Starting Middleware & CORS Demo")
    print("=" * 60 + "\n")
    yield
    print("\n" + "=" * 60)
    print("Server shutdown")
    print("=" * 60 + "\n")


app = FastAPI(title="Middleware & CORS Demo", lifespan=lifespan)

# Add middleware (order matters!)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://example.com",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,
)
app.add_middleware(auth_middleware)
app.add_middleware(log_requests_middleware)


@app.get("/")
async def health():
    """Health check"""
    return {"status": "ok", "message": "Middleware & CORS Demo"}


@app.get("/data")
async def get_data():
    """Public endpoint"""
    return {"data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}


@app.post("/login")
async def login(user: LoginRequest):
    """Login endpoint - returns token"""
    if user.username == "john" and user.password == "pass123":
        token = f"jwt-token-for-{user.username}"
        print(f"[LOGIN] ✓ {user.username} logged in")
        return {"access_token": token, "token_type": "bearer"}
    else:
        print(f"[LOGIN] ✗ Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/protected")
async def protected_route():
    """Protected endpoint (requires auth)"""
    return {"message": "Protected data"}


@app.options("/{full_path:path}")
async def preflight():
    """CORS preflight"""
    return JSONResponse(status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
