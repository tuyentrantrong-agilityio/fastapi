"""Celery tasks for async task processing.

- Process task asynchronously (delay 5-10s, update status in DB)
- Simulate long-running operation
- Support status tracking: todo -> in_progress -> done
"""

import logging
import asyncio
import random
import time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.pool import NullPool
from .celery_app import celery_app
from ..models.task import Task
from ..core.config import settings

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
                "title": task.title
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
    
    Args:
        task_id: Task ID to process
    
    Returns:
        Task result with final status
    """
    task_cid = self.request.id
    retry_count = self.request.retries
    
    logger.info(f"[RECEIVE] [process_task_async] Task received (Celery ID: {task_cid})")
    
    try:
        # Step 1: Update to in_progress
        logger.info(f"[PROCESS]  [Task {task_id}] Updating status to 'in_progress'...")
        result = run_async(_update_task_status(task_id, "in_progress"))
        if result["status"] != "success":
            raise Exception(result.get("message", "Failed to update status"))
        
        # Step 2: Simulate processing (random delay 5-10s)
        delay = random.randint(5, 10)
        logger.info(f"⏳ [Task {task_id}] Processing... (waiting {delay}s)")
        time.sleep(delay)
        
        # Step 3: Update to done
        logger.info(f"[OK] [Task {task_id}] Processing complete, updating status to 'done'...")
        result = run_async(_update_task_status(task_id, "done"))
        
        logger.info(f"[OK] [process_task_async] Task completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"[NO] [Task {task_id}] Error: {str(exc)} (Retry {retry_count + 1}/2)")
        raise self.retry(exc=exc, countdown=5)
