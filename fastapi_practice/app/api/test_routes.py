"""Test endpoints for Celery debugging and demonstration.

Only enabled when TEST_MODE=True in .env
"""

import logging
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from ..core.config import settings
from ..tasks.celery_app import celery_app
from ..tasks.email_tasks import send_welcome_email_task

router = APIRouter(prefix="/test", tags=["test"])
logger = logging.getLogger(__name__)


@router.post("/send-email")
async def test_send_email(email: str = "test@example.com"):
    """Send a single email to test Celery task.
    
    Usage: POST /test/send-email?email=myemail@example.com
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")
    
    print("\n" + "="*60)
    print("📬 CASE 1: BASIC TASK EXECUTION")
    print("="*60)
    print(f"🔔 API called: /test/send-email?email={email}")
    
    task = send_welcome_email_task.delay(email=email, user_name="TestUser")
    
    print(f"📤 Task sent to queue (ID: {task.id})")
    print("   Waiting for execution...")
    print("="*60 + "\n")
    
    return {
        "status": "queued",
        "task_id": task.id,
        "email": email,
        "message": "Email task queued. Check logs for execution."
    }


@router.post("/bulk-email")
async def test_bulk_email(count: int = 10):
    """Enqueue multiple emails to test queue and concurrency.
    
    Usage: POST /test/bulk-email?count=50
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")

    print("\n" + "="*60)
    print("⚡ CASE 4: CONCURRENCY TEST")
    print("="*60)
    print(f"🔔 API called: /test/bulk-email?count={count}")
    print(f"📬 Enqueueing {count} tasks to queue...")
    
    task_ids = []
    
    for i in range(count):
        task = send_welcome_email_task.delay(
            email=f"bulk{i}@test.example.com",
            user_name=f"BulkUser{i}"
        )
        task_ids.append(task.id)
    
    print(f"✅ All {count} tasks enqueued!")
    print(f"   📊 When worker/concurrency=4: should see 4 tasks running in parallel")
    print("="*60 + "\n")
    
    return {
        "status": "queued",
        "count": count,
        "task_ids": task_ids,
        "message": f"Enqueued {count} email tasks. Check logs for execution."
    }


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a Celery task.
    
    Usage: GET /test/task-status/abc-def-123
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")
    
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,  # PENDING, RETRY, FAILURE, SUCCESS
        "result": result.result if result.ready() else "(pending)",
        "error": str(result.info) if result.state in ["FAILURE", "RETRY"] else None,
    }


@router.post("/simulate-failure")
async def toggle_failure_simulation(enable: bool):
    """Toggle fake failure for retry testing.
    
    Usage: POST /test/simulate-failure?enable=true
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")

    print("\n" + "="*60)
    print("🔴 CASE 2: RETRY MECHANISM TEST")
    print("="*60)
    if enable:
        print("✅ Fake failure ENABLED (50% chance)")
        print("   Next /test/send-email will simulate failures")
        print("   Expected pattern:")
        print("   ❌ FAILED (attempt 1/3)")
        print("   🔄 Retry in 5s... (attempt 2/3)")
        print("   ❌ FAILED (attempt 2/3)")
        print("   🔄 Retry in 5s... (attempt 3/3)")
        print("   ✅ SUCCESS (or FAILED - max retries)")
    else:
        print("✅ Fake failure DISABLED")
        print("   All emails will send normally")
    print("="*60 + "\n")
    
    settings.FAKE_EMAIL_FAILURE = enable
    
    return {
        "fake_failure": enable,
        "message": "Fake failure simulation toggled",
        "info": "When enabled, 50% of emails will fail to test retry mechanism"
    }


@router.get("/active-tasks")
async def get_active_tasks():
    """Get number of active tasks in queue.
    
    Usage: GET /test/active-tasks
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")
    
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active()
    
    total_active = 0
    if active_tasks:
        for worker, tasks in active_tasks.items():
            total_active += len(tasks)
    
    return {
        "active_tasks_by_worker": active_tasks,
        "total_active": total_active,
        "message": f"{total_active} task(s) currently running"
    }


@router.get("/status")
async def get_celery_status():
    """Get Celery and Redis status.
    
    Usage: GET /test/status
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")
    
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    
    return {
        "test_mode": settings.TEST_MODE,
        "fake_email_failure": settings.FAKE_EMAIL_FAILURE,
        "celery_workers": stats if stats else "(no workers available)",
        "message": "If TEST_MODE=True and no workers: tasks run eagerly. Otherwise: start Celery worker"
    }
