"""Celery app configuration for background email tasks.

Phase 2: Celery + Redis (replacing BackgroundTasks)
  - Tasks queued in Redis broker
  - Dedicated workers process tasks
  - Supports retry, scaling, monitoring
"""

from celery import Celery
from ..core.config import settings

celery_app = Celery(__name__)


def configure_celery(app_name: str = "fastapi_practice"):
    """Configure Celery based on settings (TEST_MODE or PRODUCTION)"""
    celery_app.main = app_name

    if settings.TEST_MODE:
        # Test mode: eager execution, no Redis
        print("[CELERY] Running in TEST_MODE - tasks execute eagerly")
        celery_app.conf.update(
            task_always_eager=True,
            task_eager_propagates=True,
            task_eager_propagates_exceptions=True,
        )
    else:
        # Production: Redis broker, task queue, retry, monitoring
        print(f"[CELERY] Running in PRODUCTION - broker: {settings.CELERY_BROKER_URL}")
        celery_app.conf.update(
            broker_url=settings.CELERY_BROKER_URL,
            result_backend=settings.CELERY_RESULT_BACKEND,
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            task_acks_late=True,
            worker_prefetch_multiplier=4,
            task_default_retry_delay=5,  # Wait 5s before retry
            task_max_retries=3,  # Retry 3 times max
        )

    # Autodiscover tasks from all apps
    celery_app.autodiscover_tasks(["app.tasks"])


# Initialize on import
configure_celery()


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f"[DEBUG] Request: {self.request!r}")
