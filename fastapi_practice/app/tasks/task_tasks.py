"""Celery tasks for async task processing.

- Process task asynchronously (delay 5-10s, update status in DB)
- Simulate long-running operation
- Support status tracking: todo -> in_progress -> done
"""

import asyncio
import logging
import random
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from ..core.config import settings
from ..models.task import Task
from .celery_app import celery_app

logger = logging.getLogger(__name__)

# Create a dedicated async engine for Celery tasks (isolated from FastAPI's engine)
# Use NullPool to create fresh connections each time (avoid pool conflicts)
celery_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)
celery_async_session = sessionmaker(
    celery_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def _update_task_status(task_id: int, status: str) -> dict:
    """Helper: Update task status in database (async)

    Uses a dedicated database session to avoid conflicts with FastAPI's session.
    """
    try:
        async with celery_async_session() as session:
            # Fetch task
            stmt = select(Task).where(Task.id == task_id)
            result = await session.execute(stmt)
            task = result.scalars().first()

            if not task:
                logger.warning(f"Task {task_id} not found")
                return {"status": "error", "message": f"Task {task_id} not found"}

            # Update status
            task.status = status
            session.add(task)
            await session.commit()

            logger.info(f"[OK] Task {task_id} status updated to: {status}")
            return {
                "status": "success",
                "task_id": task_id,
                "task_status": status,
                "title": task.title,
            }
    except Exception as exc:
        logger.error(f"Failed to update task {task_id}: {exc}")
        raise


def run_async(coro):
    """Helper: Run async function from sync Celery task

    In TEST_MODE, Celery tasks run eagerly in the same process as FastAPI.
    Since FastAPI already has a running event loop, we need to:
    1. Detect if there's a running loop
    2. If yes, run in a separate thread (which gets its own event loop)
    3. If no, create a new loop in the current thread
    """
    import concurrent.futures

    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        # If we get here, there IS a running loop
        # So we must run async code in a separate thread
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
    except RuntimeError:
        # No running event loop, safe to create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=2, default_retry_delay=5)
def process_task_async(self, task_id: int):
    """
    Celery task: Process task asynchronously.

    Simulates long-running operation:
    1. todo -> in_progress (immediate)
    2. Wait 5-10 seconds (simulate processing)
    3. in_progress -> done

    Logs execution details to verify concurrency:
    - [TASK START] with pid, celery task_id, timestamp
    - [TASK END] with pid, celery task_id, duration

    Args:
        task_id: Task ID to process

    Returns:
        Task result with final status
    """
    start_time = time.time()
    task_cid = self.request.id
    retry_count = self.request.retries

    logger.info(f"[START] id={task_cid} task_id={task_id}")

    try:
        # Step 1: Update to in_progress
        result = run_async(_update_task_status(task_id, "in_progress"))
        if result["status"] != "success":
            raise Exception(result.get("message", "Failed to update status"))

        # Step 2: Simulate processing (random delay 5-10s)
        delay = random.randint(5, 10)
        time.sleep(delay)

        # Step 3: Update to done
        result = run_async(_update_task_status(task_id, "done"))

        duration = time.time() - start_time
        logger.info(f"[SUCCESS] id={task_cid} task_id={task_id} duration={duration:.2f}s")
        return result

    except Exception as exc:
        duration = time.time() - start_time
        logger.error(f"[ERROR] id={task_cid} task_id={task_id} error={str(exc)}")
        logger.warning(f"[RETRY] id={task_cid} retry={retry_count + 1}")
        raise self.retry(exc=exc, countdown=5)
