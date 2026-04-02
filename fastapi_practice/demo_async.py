"""
FastAPI BackgroundTasks vs Celery + Redis Demo

Usage:
  1. pip install fastapi uvicorn celery redis
  2. redis-server (or start Redis)
  3. python demo_async.py
  4. celery -A demo_async.celery worker --loglevel=info (in another terminal)

POST /register/background  - Uses FastAPI BackgroundTasks (same process)
POST /register/celery      - Uses Celery + Redis (separate worker)
"""

import time
from datetime import datetime
from celery import Celery
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager

users_db = []

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


@app.post("/register/background")
def register_with_background(
    request: UserRegisterRequest, background_tasks: BackgroundTasks
):
    """Register with BackgroundTasks - same process"""
    print(f"[API] POST /register/background for {request.email}")
    background_tasks.add_task(send_email_background, request.email)
    print(f"[API] Response sent immediately\n")

    return {
        "status": "success",
        "message": f"Request received for {request.email}",
        "method": "background_tasks",
        "note": "Task runs in same process",
    }


@app.post("/register/celery")
def register_with_celery(request: UserRegisterRequest):
    """Register with Celery - separate worker process"""
    print(f"[API] POST /register/celery for {request.email}")
    task = send_email_celery.delay(request.email)
    print(f"[API] Task queued with ID: {task.id}\n")

    return {
        "status": "accepted",
        "message": f"Request received for {request.email}",
        "method": "celery",
        "task_id": task.id,
        "note": "Task runs in separate worker process",
        "check_status": f"GET /tasks/{task.id}",
    }


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
