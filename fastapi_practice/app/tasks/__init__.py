"""Background tasks module.

Phase 1: FastAPI BackgroundTasks
  - Called from endpoints via background_tasks.add_task()
  - Runs in thread pool on same process
  - Good for learning and demo

Phase 2: Celery + Redis
  - Persistent task queue
  - Multi-worker support
  - Better error handling and retries
"""

from .email_tasks import (
    send_welcome_email_task,
    send_task_assigned_email_task,
)
from .task_tasks import (
    process_task_async,
)

__all__ = [
    "send_welcome_email_task",
    "send_task_assigned_email_task",
    "process_task_async",
]
