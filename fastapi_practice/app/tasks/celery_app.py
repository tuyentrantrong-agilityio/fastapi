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
    """Configure Celery with Redis broker & async execution.

    IMPORTANT: Both TEST_MODE=True and TEST_MODE=False use the SAME Celery config!

    [OK] Redis broker: Same URL for both modes
    [OK] Async execution: Both modes queue tasks to Redis
    [OK] Worker processing: Both modes need separate celery worker
    [OK] Task persistence: Both modes save to Redis
    [OK] Retry mechanism: Both modes support retries
    [OK] Parallel processing: Both modes support concurrency

    ONLY DIFFERENCE:
    [NO] TEST_MODE=True: Test endpoints (/test/*) ENABLED
    [NO] TEST_MODE=False: Test endpoints (/test/*) DISABLED (403)

    This ensures:
    - Development team can test Celery/Redis in practice mode
    - Test endpoints won't leak into production (TEST_MODE=false)
    - Code remains identical - only configuration toggles endpoints
    """
    celery_app.main = app_name

    # ========== ASYNC CONFIGURATION (BOTH MODES) ==========
    # Celery + Redis configured for async task queue
    # Requires: Redis server + Celery worker running

    import logging

    logger = logging.getLogger(__name__)

    # Use logging instead of print to avoid stdout contamination
    # (print interferes with JSON generation for OpenAPI export)
    logger.info("[CELERY] Production-Ready Async Configuration")
    logger.info(f"  [OK] Broker: {settings.CELERY_BROKER_URL}")
    logger.info(f"  [OK] Result backend: {settings.CELERY_RESULT_BACKEND}")
    logger.info("  [OK] Tasks: ASYNC (queued to Redis)")
    logger.info("  [OK] Workers: Processes tasks from queue")
    logger.info("  [OK] Concurrency: Parallel processing (4 default)")
    logger.info("  [OK] Persistence: Tasks saved to Redis")
    logger.info("  [OK] Retry: Supported (3 retries, 5s backoff)")
    if settings.TEST_MODE:
        logger.info("  [ENABLED] Test endpoints (/test/*) ENABLED")
    else:
        logger.info("  [DISABLED] Test endpoints (/test/*) DISABLED")

    # Same config for both TEST_MODE=true and TEST_MODE=false
    celery_app.conf.update(
        broker_url=settings.CELERY_BROKER_URL,  # Redis broker save tasks
        result_backend=settings.CELERY_RESULT_BACKEND,  # Redis backend save results
        broker_connection_retry_on_startup=False,  # Don't hang on startup if broker down
        broker_connection_retry=True,
        broker_connection_max_retries=3,  # Retry 3 times, fail fast
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
