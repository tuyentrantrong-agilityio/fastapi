"""Internal integration test endpoints for Celery + Redis verification.

Only enabled when TEST_MODE=True in .env (development/staging only)

INTERNAL USE ONLY - Not for production

These endpoints allow real-world testing of:
- Celery task queueing to Redis
- Worker execution and retry mechanism
- Concurrency and throughput
- End-to-end async pipeline
"""

import logging

from fastapi import APIRouter, HTTPException
from redis.asyncio import from_url
from redis.exceptions import ConnectionError as RedisConnectionError

from ..core.config import settings
from ..tasks.email_tasks import send_welcome_email_task

router = APIRouter(prefix="/internal", tags=[" Internal Tools (Dev/Staging Only)"])
logger = logging.getLogger(__name__)


@router.post("/send-email")
async def internal_send_email(email: str = "test@example.com"):
    """[INTERNAL ONLY] Trigger email task to verify end-to-end pipeline.

    Verifies: FastAPI → Redis → Celery Worker pipeline

    Usage: POST /internal/send-email?email=myemail@example.com

    Only available when TEST_MODE=True
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Internal tools disabled (TEST_MODE=False)")

    print("\n" + "=" * 60)
    print("[INTERNAL] Email Task Pipeline Test")
    print("=" * 60)
    print(f" Endpoint: POST /internal/send-email?email={email}")
    logger.info(f" Test endpoint called: /test/send-email?email={email}")

    try:
        print("[QUEUE] Queuing task to Redis...")
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
                "help": "Start Redis: redis-server, then start Celery worker: celery -A app.tasks.celery_app worker -l info",
            },
        )
    except Exception as e:
        error_msg = f"[NO] ERROR: {e}"
        print(error_msg)
        logger.error(f"[NO] Error queueing task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")


@router.post("/bulk-email")
async def internal_bulk_email(count: int = 10):
    """[INTERNAL ONLY] Queue multiple email tasks to test concurrency and throughput.

    Verifies: Queue behavior, worker concurrency, task throughput

    Usage: POST /internal/bulk-email?count=50

    Watch worker logs to see parallel processing (default: 4 workers)
    Only available when TEST_MODE=True
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Internal tools disabled (TEST_MODE=False)")

    print("\n" + "=" * 60)
    print("[INTERNAL] Concurrency & Queue Test")
    print("=" * 60)
    print(f"[ENDPOINT] POST /internal/bulk-email?count={count}")
    print(f"[ENQUEUE] Enqueueing {count} tasks to queue...")

    task_ids = []

    for i in range(count):
        task = send_welcome_email_task.delay(
            email=f"bulk{i}@test.example.com", user_name=f"BulkUser{i}"
        )
        task_ids.append(task.id)

    print(f"[OK] All {count} tasks enqueued!")
    print("   [STATS] When worker/concurrency=4: should see 4 tasks running in parallel")
    print("=" * 60 + "\n")

    return {
        "status": "queued",
        "count": count,
        "task_ids": task_ids,
        "message": f"Enqueued {count} email tasks. Check logs for execution.",
    }


@router.post("/simulate-failure")
async def internal_simulate_failure(enable: bool):
    """[INTERNAL ONLY] Enable/disable simulated email failures to test retry mechanism.

    When enabled: FAKE_FAILURE_RATE % of email tasks will fail to trigger Celery retry logic

    Verifies: Retry delays, max_retries, exponential backoff

    Usage:
        POST /internal/simulate-failure?enable=true   # Enable failures
        POST /internal/send-email                      # Will fail and retry
        POST /internal/simulate-failure?enable=false   # Disable failures

    Only available when TEST_MODE=True
    """
    if not settings.TEST_MODE:
        raise HTTPException(status_code=403, detail="Internal tools disabled (TEST_MODE=False)")

    print("\n" + "=" * 60)
    print("[INTERNAL] Retry Mechanism Test")
    print("=" * 60)

    try:
        # Save to Redis so Celery worker can read it
        redis = await from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        await redis.set("test:fake_email_failure", str(enable))
        await redis.close()

        if enable:
            print("[OK] Simulated failures ENABLED")
            print("   Next /internal/send-email will simulate failures")
            print(f"   Failure rate: {settings.FAKE_FAILURE_RATE * 100:.0f}%")
            print("   Expected pattern:")
            print("   [TEST-FAIL] Simulating failure")
            print("   [RETRY] Retry in 5s... (attempt 1/3)")
            print("   [TEST-FAIL] Simulating failure")
            print("   [RETRY] Retry in 5s... (attempt 2/3)")
            print("   [OK] SUCCESS (or FAILED - max retries)")
        else:
            print("[OK] Fake failure DISABLED")
            print("   All emails will send normally")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to update Redis: {e}")
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

    return {
        "fake_failure": enable,
        "message": "Fake failure simulation toggled via Redis",
        "info": f"When enabled, {settings.FAKE_FAILURE_RATE * 100:.0f}% of emails will fail to test retry mechanism",
    }
