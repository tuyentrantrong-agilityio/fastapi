"""Background email tasks - using Celery instead of BackgroundTasks.

Phase 2: Celery + Redis (with async-native Celery tasks)
  - Tasks queued in Redis broker
  - Workers process asynchronously
  - Supports retry, monitoring
  - Native async support (no nested event loop issues)
"""

import logging
import random
import asyncio
import concurrent.futures
from .celery_app import celery_app
from ..services.email_service import email_service
from ..core.config import settings

logger = logging.getLogger(__name__)


# ============ Task Lifecycle Logging ============
def log_task_received(task_name: str, task_id: str, email: str):
    """Log: Task received from queue"""
    print(f"📥 [{task_name}] RECEIVED from queue")
    print(f"   └─ Task ID: {task_id}")
    print(f"   └─ Email: {email}")
    logger.info(f"📥 Task received: {task_name} (ID: {task_id})")


def log_task_started(task_name: str, retry_count: int = 0):
    """Log: Task execution started"""
    if retry_count == 0:
        print(f"⚙️  [{task_name}] PROCESSING...")
    else:
        print(f"🔄 [{task_name}] RETRY #{retry_count + 1} of 3...")
    logger.info(f"⚙️  Task started: {task_name} (Retry: {retry_count})")


def log_task_success(email: str):
    """Log: Task completed successfully"""
    print(f"✅ EMAIL SENT to {email}")
    logger.info(f"✅ Task completed: Email sent")


def log_task_failed(email: str, error: str, retry_count: int):
    """Log: Task failed (will retry or fail permanently)"""
    if retry_count < 2:
        print(f"❌ FAILED: {email}")
        print(f"   └─ Error: {error}")
        print(f"   └─ 🔄 Retrying in 5s... (Attempt {retry_count + 2}/3)")
        logger.warning(f"❌ Task failed, retry {retry_count + 2}/3: {error}")
    else:
        print(f"💥 FAILED (NO MORE RETRIES): {email}")
        print(f"   └─ Error: {error}")
        logger.error(f"💥 Task failed permanently: {error}")


def log_queue_status(action: str, count: int = None):
    """Log: Queue status"""
    if action == "enqueued":
        print(f"📬 ENQUEUED {count} task(s) to queue")
        logger.info(f"📬 Task(s) enqueued: {count}")
    elif action == "processing":
        print(f"⚙️  PROCESSING {count} active task(s)...")
        logger.info(f"⚙️  Processing: {count} tasks")



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
async def _send_welcome_email(email: str, user_name: str = "User", retry_count: int = 0):
    """Internal: Send welcome email (async)"""
    
    # TEST: Fake failure to test retry mechanism
    if settings.TEST_MODE and settings.FAKE_EMAIL_FAILURE:
        if random.random() < settings.FAKE_FAILURE_RATE:
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
        logger.info(f"[✓] Welcome email sent to {email}")
        return {"status": "sent", "email": email}
    else:
        raise Exception("Email service failed")


async def _send_password_reset_email(email: str, reset_link: str, user_name: str = "User", retry_count: int = 0):
    """Internal: Send password reset email (async)"""
    logger.info(f"[CELERY-TASK] send_password_reset_email_task STARTED")
    logger.debug(f"  Email: {email}, User: {user_name}, Retry: {retry_count}")
    
    if settings.TEST_MODE and settings.FAKE_EMAIL_FAILURE:
        if random.random() < settings.FAKE_FAILURE_RATE:
            logger.warning(f"[CELERY-TEST] Simulating failure for {email} (attempt #{retry_count + 1})")
            raise Exception(f"[FAKE] Simulated failure (attempt #{retry_count + 1})")
    
    subject = "Reset Your Password - FastAPI Practice"
    html_content = f"""
<html>
    <body style="font-family: Arial, sans-serif;">
        <h1>Password Reset Request</h1>
        <p>Hi {user_name},</p>
        <p>We received a request to reset your password.</p>
        <p>
            <a href="{reset_link}" 
               style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Reset Password
            </a>
        </p>
        <p style="color: #666;">This link expires in 30 minutes.</p>
        <p style="color: #666; font-size: 12px;">
            If you didn't request a password reset, please ignore this email.
        </p>
    </body>
</html>
    """
    plain_content = f"""
Password Reset Request

Hi {user_name},

Click here to reset your password:
{reset_link}

This link expires in 30 minutes.

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
        logger.info(f"[CELERY-SUCCESS] Password reset email sent to {email}")
        return {"status": "sent", "email": email}
    else:
        raise Exception("Email service returned False")


async def _send_task_assigned_email(
    email: str, user_name: str, task_title: str, task_id: int, assigned_by: str = "System", retry_count: int = 0
):
    """Internal: Send task assignment notification email (async)"""
    logger.info(f"[CELERY-TASK] send_task_assigned_email_task STARTED")
    logger.debug(f"  Email: {email}, Task: {task_title} (ID: {task_id}), Assigned by: {assigned_by}, Retry: {retry_count}")
    
    if settings.TEST_MODE and settings.FAKE_EMAIL_FAILURE:
        if random.random() < settings.FAKE_FAILURE_RATE:
            logger.warning(f"[CELERY-TEST] Simulating failure for {email} (attempt #{retry_count + 1})")
            raise Exception(f"[FAKE] Simulated failure (attempt #{retry_count + 1})")
    
    subject = f"New Task Assigned: {task_title}"
    html_content = f"""
<html>
    <body style="font-family: Arial, sans-serif;">
        <h1>Task Assigned to You 📋</h1>
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
    task_id = self.request.id
    retry_count = self.request.retries
    
    # Log: Task received
    log_task_received("send_welcome_email_task", task_id, email)
    log_task_started("send_welcome_email_task", retry_count)
    
    try:
        result = run_async(_send_welcome_email(email, user_name, retry_count=retry_count))
        log_task_success(email)
        return result
    except Exception as exc:
        log_task_failed(email, str(exc), retry_count)
        raise self.retry(exc=exc, countdown=5)


@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=3, default_retry_delay=5)
def send_password_reset_email_task(self, email: str, reset_link: str, user_name: str = "User"):
    """Send password reset email."""
    logger.info(f"[CELERY] ===== Task send_password_reset_email_task QUEUED =====")
    try:
        result = run_async(_send_password_reset_email(email, reset_link, user_name, retry_count=self.request.retries))
        logger.info(f"[CELERY] ===== Task send_password_reset_email_task COMPLETED =====")
        return result
    except Exception as exc:
        logger.error(f"[CELERY-ERROR] Task failed: {str(exc)}")
        logger.info(f"[CELERY] ===== Retrying (attempt #{self.request.retries + 1}/3) =====")
        raise self.retry(exc=exc, countdown=5)


@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=3, default_retry_delay=5)
def send_task_assigned_email_task(
    self, email: str, user_name: str, task_title: str, task_id: int, assigned_by: str = "System"
):
    """Send task assignment notification email."""
    logger.info(f"[CELERY] ===== Task send_task_assigned_email_task QUEUED =====")
    try:
        result = run_async(
            _send_task_assigned_email(email, user_name, task_title, task_id, assigned_by, retry_count=self.request.retries)
        )
        logger.info(f"[CELERY] ===== Task send_task_assigned_email_task COMPLETED =====")
        return result
    except Exception as exc:
        logger.error(f"[CELERY-ERROR] Task failed: {str(exc)}")
        logger.info(f"[CELERY] ===== Retrying (attempt #{self.request.retries + 1}/3) =====")
        raise self.retry(exc=exc, countdown=5)
