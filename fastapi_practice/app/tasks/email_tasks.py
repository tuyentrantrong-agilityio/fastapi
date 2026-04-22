"""Background email tasks - using Celery instead of BackgroundTasks.

Phase 2: Celery + Redis (with async-native Celery tasks)
  - Tasks queued in Redis broker
  - Workers process asynchronously
  - Supports retry, monitoring
  - Native async support (no nested event loop issues)
"""

import asyncio
import concurrent.futures
import logging
import random
import time

from redis.asyncio import from_url

from ..core.config import settings
from ..services.email_service import email_service
from .celery_app import celery_app

logger = logging.getLogger(__name__)


# Production-ready logging (no helper functions needed)


def run_async(coro):
    """Helper: Run async function from sync Celery task safely.

    When called from TEST_MODE eager execution:
    - Detects running event loop
    - Runs async code in separate thread with own event loop
    - No conflicts, no hangs!
    """
    try:
        # Try standard asyncio.run() first (works in production, no running loop)
        return asyncio.run(coro)
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            # Running loop detected (TEST_MODE eager execution in FastAPI)
            # Solution: Run in separate thread with its own event loop
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()

            # Execute in thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        raise


# Async email task functions (helper functions)
async def _should_simulate_failure() -> bool:
    """Check if email failure should be simulated.

    Priority:
    1. Check Redis key (set by /internal/simulate-failure endpoint)
    2. Fall back to .env FAKE_EMAIL_FAILURE
    """
    try:
        redis = await from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        redis_value = await redis.get("test:fake_email_failure")
        await redis.close()

        if redis_value is not None:
            return redis_value.lower() == "true"
    except Exception as e:
        logger.debug(f"Redis check failed, using .env: {e}")

    # Fall back to .env
    return settings.FAKE_EMAIL_FAILURE


async def _send_welcome_email(email: str, user_name: str = "User", retry_count: int = 0):
    """Internal: Send welcome email (async)"""

    # TEST: Fake failure to test retry mechanism
    if settings.TEST_MODE:
        should_fail = await _should_simulate_failure()
        if should_fail and random.random() < settings.FAKE_FAILURE_RATE:
            logger.info(f"[TEST-FAIL] Simulating failure for {email} (attempt #{retry_count + 1})")
            raise Exception(f"[FAKE] Simulated failure (attempt #{retry_count + 1})")

    subject = "Welcome to FastAPI Practice!"
    html_content = f"""
<html>
    <body style="font-family: Arial, sans-serif;">
        <h1>Welcome, {user_name}! 🎉</h1>
        <p>Thank you for registering with our FastAPI Practice application.</p>
        <p>Your account is ready to use. Start creating tasks and projects!</p>
        <hr />
        <p style="color: #666; font-size: 12px;">
            If you didn't register for this account, please ignore this email.
        </p>
    </body>
</html>
    """
    plain_content = f"""
Welcome, {user_name}!

Thank you for registering. Your account is ready to use.
Start creating tasks and projects!

Regards,
FastAPI Practice Team
    """

    success = await email_service.send_email(
        to=email,
        subject=subject,
        html_content=html_content,
        plain_content=plain_content,
    )
    logger.debug(f"  Email service returned: {success}")

    if success:
        logger.info(f"[OK] Welcome email sent to {email}")
        return {"status": "sent", "email": email}
    else:
        raise Exception("Email service failed")


async def _send_task_assigned_email(
    email: str,
    user_name: str,
    task_title: str,
    task_id: int,
    assigned_by: str = "System",
    retry_count: int = 0,
):
    """Internal: Send task assignment notification email (async)"""
    logger.info("[CELERY-TASK] send_task_assigned_email_task STARTED")
    logger.debug(
        f"  Email: {email}, Task: {task_title} (ID: {task_id}), Assigned by: {assigned_by}, Retry: {retry_count}"
    )

    if settings.TEST_MODE:
        should_fail = await _should_simulate_failure()
        if should_fail and random.random() < settings.FAKE_FAILURE_RATE:
            logger.warning(
                f"[CELERY-TEST] Simulating failure for {email} (attempt #{retry_count + 1})"
            )
            raise Exception(f"[FAKE] Simulated failure (attempt #{retry_count + 1})")

    subject = f"New Task Assigned: {task_title}"
    html_content = f"""
<html>
    <body style="font-family: Arial, sans-serif;">
        <h1>Task Assigned to You [LIST]</h1>
        <p>Hi {user_name},</p>
        <p><strong>{assigned_by}</strong> assigned you a new task:</p>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h3>{task_title}</h3>
            <p><small>Task ID: {task_id}</small></p>
        </div>
        <p>Log in to the application to view details and update progress.</p>
    </body>
</html>
    """
    plain_content = f"""
Task Assigned to You

Hi {user_name},

{assigned_by} assigned you a new task:

{task_title}
Task ID: {task_id}

Log in to view details.

Regards,
FastAPI Practice Team
    """

    success = await email_service.send_email(
        to=email,
        subject=subject,
        html_content=html_content,
        plain_content=plain_content,
    )
    logger.debug(f"  Email service returned: {success}")

    if success:
        logger.info(f"[CELERY-SUCCESS] Task assignment email sent to {email}")
        return {"status": "sent", "email": email, "task_id": task_id}
    else:
        raise Exception("Email service returned False")


# Celery async tasks (using newly added async support)
# These get converted to sync tasks but internally support awaiting async functions
@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=3, default_retry_delay=5)
def send_welcome_email_task(self, email: str, user_name: str = "User"):
    """Send welcome email after user registration - Celery task."""
    start_time = time.time()
    task_id = self.request.id
    retry_count = self.request.retries

    logger.info(f"[START] id={task_id} email={email}")

    try:
        # Simulate workload for 3-5 seconds to observe concurrency
        sleep_time = 3 if retry_count == 0 else 2
        time.sleep(sleep_time)

        result = run_async(_send_welcome_email(email, user_name, retry_count=retry_count))

        duration = time.time() - start_time
        logger.info(f"[SUCCESS] id={task_id} email={email} duration={duration:.2f}s")
        return result
    except Exception as exc:
        duration = time.time() - start_time
        logger.error(f"[ERROR] id={task_id} email={email} error={str(exc)}")
        logger.warning(f"[RETRY] id={task_id} retry={retry_count + 1}")
        raise self.retry(exc=exc, countdown=5)


@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=3, default_retry_delay=5)
def send_task_assigned_email_task(
    self,
    email: str,
    user_name: str,
    task_title: str,
    task_id: int,
    assigned_by: str = "System",
):
    """Send task assignment notification email."""
    start_time = time.time()
    celery_task_id = self.request.id
    retry_count = self.request.retries

    logger.info(f"[START] id={celery_task_id} email={email}")

    try:
        # Simulate workload for 3-5 seconds
        sleep_time = 3 if retry_count == 0 else 2
        time.sleep(sleep_time)

        result = run_async(
            _send_task_assigned_email(
                email,
                user_name,
                task_title,
                task_id,
                assigned_by,
                retry_count=retry_count,
            )
        )

        duration = time.time() - start_time
        logger.info(f"[SUCCESS] id={celery_task_id} email={email} duration={duration:.2f}s")
        return result
    except Exception as exc:
        duration = time.time() - start_time
        logger.error(f"[ERROR] id={celery_task_id} email={email} error={str(exc)}")
        logger.warning(f"[RETRY] id={celery_task_id} retry={retry_count + 1}")
        raise self.retry(exc=exc, countdown=5)
