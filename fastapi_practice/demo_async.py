"""
FastAPI BackgroundTasks vs Celery + Redis Demo
With Caching & Rate Limiting

Usage:
  1. pip install fastapi uvicorn celery redis slowapi
  2. redis-server (or start Redis)
  3. python demo_async.py
  4. celery -A demo_async.celery worker --loglevel=info (in another terminal)

Features:
  POST /register/background  - BackgroundTasks (same process) + cache (5 reqs/min)
  POST /register/celery      - Celery worker (separate process) + cache (5 reqs/min)
  GET  /tasks/{task_id}      - Celery task status
  GET  /users                - List all users
  GET  /                     - Health check
"""

import time
import json
from datetime import datetime
from celery import Celery
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import redis
from slowapi import Limiter
from slowapi.util import get_remote_address

users_db = []
redis_client = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)
limiter = Limiter(key_func=get_remote_address)

celery_app = Celery(
    __name__, broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


class UserRegisterRequest(BaseModel):
    email: str


def send_email_background(email: str) -> None:
    """Background task - runs in same process"""
    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\n[BACKGROUND] Starting for {email} at {now}")

    time.sleep(3)

    users_db.append(
        {
            "email": email,
            "method": "background_tasks",
            "created_at": datetime.now().isoformat(),
        }
    )

    print(f"[BACKGROUND] ✓ Email sent to {email}")


@celery_app.task(bind=True, max_retries=3)
def send_email_celery(self, email: str) -> dict:
    """Celery task - runs in separate worker process"""
    try:
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[CELERY] Starting for {email} at {now}")
        print(f"[CELERY] Task ID: {self.request.id}")

        time.sleep(3)

        users_db.append(
            {
                "email": email,
                "method": "celery",
                "task_id": self.request.id,
                "created_at": datetime.now().isoformat(),
            }
        )

        print(f"[CELERY] ✓ Email sent to {email}\n")

        return {"status": "success", "email": email, "task_id": self.request.id}
    except Exception as exc:
        print(f"[CELERY] ✗ Error: {str(exc)}")
        print(f"[CELERY] Retry {self.request.retries + 1}/3\n")
        raise self.retry(exc=exc, countdown=5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("\n" + "=" * 60)
    print(" Server starting...")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("Endpoints: POST /register/background, POST /register/celery")
    print("=" * 60 + "\n")

    yield

    print("\n" + "=" * 60)
    print(" Server stopping...")
    print("=" * 60 + "\n")


app = FastAPI(title="BackgroundTasks vs Celery Demo", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(429, lambda r, e: {"error": "Rate limit exceeded"})


@limiter.limit("5/minute")
@app.post("/register/background")
def register_with_background(
    request: UserRegisterRequest, background_tasks: BackgroundTasks
):
    """Register with BackgroundTasks - same process (5 requests/minute)"""
    cached = redis_client.get(f"user:{request.email}")
    if cached:
        print(f"[CACHE] Found user {request.email} in Redis")
        return json.loads(cached)

    print(f"[API] POST /register/background for {request.email}")
    background_tasks.add_task(send_email_background, request.email)
    print(f"[API] Response sent immediately\n")

    response = {
        "status": "success",
        "message": f"Request received for {request.email}",
        "method": "background_tasks",
        "note": "Task runs in same process",
    }
    redis_client.setex(f"user:{request.email}", 300, json.dumps(response))
    return response


@limiter.limit("5/minute")
@app.post("/register/celery")
def register_with_celery(request: UserRegisterRequest):
    """Register with Celery - separate worker process (5 requests/minute)"""
    cached = redis_client.get(f"user:{request.email}")
    if cached:
        print(f"[CACHE] Found user {request.email} in Redis")
        return json.loads(cached)

    print(f"[API] POST /register/celery for {request.email}")
    task = send_email_celery.delay(request.email)
    print(f"[API] Task queued with ID: {task.id}\n")

    response = {
        "status": "accepted",
        "message": f"Request received for {request.email}",
        "method": "celery",
        "task_id": task.id,
        "note": "Task runs in separate worker process",
        "check_status": f"GET /tasks/{task.id}",
    }
    redis_client.setex(f"user:{request.email}", 300, json.dumps(response))
    return response


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Check Celery task status"""
    task = send_email_celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None,
    }


@app.get("/users")
def get_users():
    """Get all registered users"""
    return {"total": len(users_db), "users": users_db}


@app.get("/")
def health():
    """Health check"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
