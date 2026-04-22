"""Tests for task_tasks.py module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestTaskTasksCoverage:
    """Tests to increase task_tasks.py coverage."""

    @pytest.mark.asyncio
    async def test_process_task_basic(self):
        """Test task processing execution path."""
        with patch("app.db.session.AsyncSessionLocal") as mock_session_factory:
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory.return_value = mock_session

            mock_task = MagicMock()
            mock_task.id = 1
            mock_task.status = "todo"

            mock_execute = MagicMock()
            mock_execute.scalar_one_or_none.return_value = mock_task
            mock_session.execute = MagicMock(return_value=mock_execute)
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            from app.tasks.task_tasks import process_task_async

            result = process_task_async(1)

    @pytest.mark.asyncio
    async def test_process_task_not_found(self):
        """Test processing non-existent task."""
        with patch("app.db.session.AsyncSessionLocal") as mock_session_factory:
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory.return_value = mock_session

            mock_execute = MagicMock()
            mock_execute.scalar_one_or_none.return_value = None
            mock_session.execute = MagicMock(return_value=mock_execute)

            from app.tasks.task_tasks import process_task_async

            result = process_task_async(999)
