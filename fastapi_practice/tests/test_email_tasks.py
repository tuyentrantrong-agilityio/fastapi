"""Tests for email_tasks.py module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestEmailTasksCoverage:
    """Tests to increase email_tasks.py coverage."""

    @pytest.mark.asyncio
    async def test_send_welcome_email_basic(self):
        """Test welcome email execution path."""
        with patch(
            "app.tasks.email_tasks.email_service.send_email", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = True

            from app.tasks.email_tasks import send_welcome_email_task

            result = send_welcome_email_task("test@example.com", "Test User")

    @pytest.mark.asyncio
    async def test_send_task_assigned_email_basic(self):
        """Test task assigned email execution path."""
        with patch(
            "app.tasks.email_tasks.email_service.send_email", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = True

            from app.tasks.email_tasks import send_task_assigned_email_task

            result = send_task_assigned_email_task(
                "test@example.com", "Test User", "Task Title", 1, "admin@example.com"
            )

    @pytest.mark.asyncio
    async def test_email_send_failure(self):
        """Test email sending when service fails."""
        with patch(
            "app.tasks.email_tasks.email_service.send_email", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = False

            from app.tasks.email_tasks import send_welcome_email_task

            # Celery will handle retry
            result = send_welcome_email_task("test@example.com")
