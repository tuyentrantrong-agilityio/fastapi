"""Test endpoints for Celery debugging and demonstration.

Only enabled when TEST_MODE=True in .env
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult
from redis.exceptions import ConnectionError as RedisConnectionError
from ..core.config import settings
from ..tasks.celery_app import celery_app
from ..tasks.email_tasks import send_welcome_email_task
from ..models.task import Task
from ..db.session import get_async_session

router = APIRouter(prefix="/test", tags=["test"])
logger = logging.getLogger(__name__)


@router.post("/send-email")
async def test_send_email(email: str = "test@example.com"):
    """Send a single email to test Celery task.

    Usage: POST /test/send-email?email=myemail@example.com
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")

    print("\n" + "=" * 60)
    print("[ENQUEUE] CASE 1: BASIC TASK EXECUTION")
    print("=" * 60)
    print(f"🔔 API called: /test/send-email?email={email}")
    logger.info(f"🔔 Test endpoint called: /test/send-email?email={email}")

    try:
        print("📤 Queuing task to Redis...")
        task = send_welcome_email_task.delay(email=email, user_name="TestUser")
        print(f"[OK] Task queued! (ID: {task.id})")
        logger.info(f"[OK] Task queued: {task.id}")
        print("   Check Celery worker console for execution logs...")
        print("=" * 60 + "\n")

        return {
            "status": "queued",
            "task_id": task.id,
            "email": email,
            "message": "Email task queued. Check Celery worker logs for execution.",
        }
    except (RedisConnectionError, RuntimeError) as e:
        error_msg = f"[NO] Redis/Celery Connection Error: {str(e)}"
        print(error_msg)
        print("\n[WARN]  TROUBLESHOOTING:")
        print("1. Is Redis running? Try: redis-cli ping")
        print("2. If not: Start Redis with: redis-server")
        print("3. Celery worker MUST also be running separately")
        print("=" * 60 + "\n")
        logger.error(f"[NO] Redis connection failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Redis/Celery not available",
                "reason": str(e),
                "help": "Start Redis: redis-server, then start Celery worker: celery -A app.tasks.celery_app worker -l info"
            }
        )
    except Exception as e:
        error_msg = f"[NO] ERROR: {e}"
        print(error_msg)
        logger.error(f"[NO] Error queueing task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")


@router.post("/bulk-email")
async def test_bulk_email(count: int = 10):
    """Enqueue multiple emails to test queue and concurrency.

    Usage: POST /test/bulk-email?count=50
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")

    print("\n" + "=" * 60)
    print("⚡ CASE 4: CONCURRENCY TEST")
    print("=" * 60)
    print(f"🔔 API called: /test/bulk-email?count={count}")
    print(f"[ENQUEUE] Enqueueing {count} tasks to queue...")

    task_ids = []

    for i in range(count):
        task = send_welcome_email_task.delay(
            email=f"bulk{i}@test.example.com", user_name=f"BulkUser{i}"
        )
        task_ids.append(task.id)

    print(f"[OK] All {count} tasks enqueued!")
    print(f"   [STATS] When worker/concurrency=4: should see 4 tasks running in parallel")
    print("=" * 60 + "\n")

    return {
        "status": "queued",
        "count": count,
        "task_ids": task_ids,
        "message": f"Enqueued {count} email tasks. Check logs for execution.",
    }


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: int, session: AsyncSession = Depends(get_async_session)):
    """Get status of a task from database.

    Usage: GET /test/task-status/2
    
    Returns task status from database instead of Celery result backend
    (which may not be configured in TEST_MODE).
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")

    # Get task from database
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return {
        "task_id": task_id,
        "title": task.title,
        "status": task.status,  # Database status: todo, in_progress, done
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.post("/simulate-failure")
async def toggle_failure_simulation(enable: bool):
    """Toggle fake failure for retry testing.

    Usage: POST /test/simulate-failure?enable=true
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")

    print("\n" + "=" * 60)
    print("🔴 CASE 2: RETRY MECHANISM TEST")
    print("=" * 60)
    if enable:
        print("[OK] Fake failure ENABLED (50% chance)")
        print("   Next /test/send-email will simulate failures")
        print("   Expected pattern:")
        print("   [NO] FAILED (attempt 1/3)")
        print("   [RETRY] Retry in 5s... (attempt 2/3)")
        print("   [NO] FAILED (attempt 2/3)")
        print("   [RETRY] Retry in 5s... (attempt 3/3)")
        print("   [OK] SUCCESS (or FAILED - max retries)")
    else:
        print("[OK] Fake failure DISABLED")
        print("   All emails will send normally")
    print("=" * 60 + "\n")

    settings.FAKE_EMAIL_FAILURE = enable

    return {
        "fake_failure": enable,
        "message": "Fake failure simulation toggled",
        "info": "When enabled, 50% of emails will fail to test retry mechanism",
    }


@router.get("/active-tasks")
async def get_active_tasks():
    """Get Celery and Redis status.

    Usage: GET /test/active-tasks
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")

    return {
        "mode": f"TEST_MODE={settings.TEST_MODE}",
        "celery_execution": "ASYNC (Redis queue)",
        "celery_broker": settings.CELERY_BROKER_URL,
        "celery_result_backend": settings.CELERY_RESULT_BACKEND,
        "redis_required": True,
        "worker_required": True,
        "info": "Tasks MUST be queued to Redis. Redis server + Celery worker REQUIRED!",
        "requirements": {
            "redis_server": "Required - redis-server",
            "celery_worker": "Required - celery -A app.tasks.celery_app worker -l info",
            "fastapi_app": "Required - uvicorn app.main:app --reload"
        }
    }


@router.get("/status")
async def get_celery_status():
    """Get Celery configuration status.

    Usage: GET /test/status
    
    Shows Redis broker & Redis result backend configuration.
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Test mode is disabled")

    return {
        "mode": f"TEST_MODE={settings.TEST_MODE}",
        "test_endpoints_enabled": settings.TEST_MODE,
        "celery_execution_mode": "ASYNC (Redis queue)",
        "celery_broker_url": settings.CELERY_BROKER_URL,
        "celery_result_backend_url": settings.CELERY_RESULT_BACKEND,
        "fake_email_failure_enabled": settings.FAKE_EMAIL_FAILURE,
        "fake_failure_rate": settings.FAKE_FAILURE_RATE,
        "requirements": {
            "redis_server": "[OK] Required & MUST be running",
            "celery_worker": "[OK] Required & MUST be running",
            "fastapi_app": "[OK] Running (this is it!)"
        },
        "troubleshooting": {
            "if_hanging": "Check Redis: redis-cli ping (should return PONG)",
            "if_no_logs": "Check Celery worker running in separate terminal",
            "if_connection_error": "Make sure redis-server is started FIRST"
        }
    }
