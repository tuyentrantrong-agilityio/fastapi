"""JSON structured logging configuration.

Provides production-ready JSON logging for all application events.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs JSON format"""

    def format(self, record: logging.LogRecord) -> str:
        """Convert log record to JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "method"):
            log_data["method"] = record.method

        if hasattr(record, "path"):
            log_data["path"] = record.path

        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        if hasattr(record, "duration_seconds"):
            log_data["duration_seconds"] = record.duration_seconds

        if hasattr(record, "error"):
            log_data["error"] = record.error

        if hasattr(record, "error_type"):
            log_data["error_type"] = record.error_type

        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id

        if hasattr(record, "task_name"):
            log_data["task_name"] = record.task_name

        if hasattr(record, "status"):
            log_data["status"] = record.status

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_json_logging(use_json: bool = False) -> None:
    """
    Configure JSON logging for the application.

    Args:
        use_json: If True, use JSON format. If False, use readable format.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Set formatter based on preference
    if use_json:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    logging.getLogger("app").setLevel(logging.DEBUG)
    logging.getLogger("app.middleware.logging_middleware").setLevel(logging.DEBUG)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)

    # Debug: Verify setup
    logging.info(f"[OK] LOGGING SETUP DONE - use_json={use_json}, handlers={root_logger.handlers}")
    logging.info("[OK] Logging initialized")
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
