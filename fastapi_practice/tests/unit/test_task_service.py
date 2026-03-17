"""Unit tests for task service functions."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.services.task_service import (
    create_task_service,
    get_user_tasks_filtered_service,
    update_task_service,
    delete_task_service,
)
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatus
from app.core.exceptions import NotFoundException, ForbiddenException


@pytest.fixture
def sample_task():
    """Sample task from database."""
    return {
        "id": 1,
        "user_id": 1,
        "title": "Test Task",
        "description": "Test Description",
        "status": "todo",
        "project_id": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


class TestCreateTaskService:
    """Test create_task_service function."""

    @pytest.mark.asyncio
    async def test_create_task_success(self):
        """Should successfully create task."""
        with (
            patch("app.services.task_service.tasks_db", {}),
            patch("app.services.task_service.task_id_counter", {"id": 1}),
            patch("app.services.task_service.datetime") as mock_datetime,
        ):
            mock_datetime.now.return_value = datetime(2024, 1, 1, tzinfo=timezone.utc)

            task_create = TaskCreate(
                title="New Task",
                description="Task Description",
                status=TaskStatus.TODO,
            )

            result = await create_task_service(task_create, 1)

            assert result["title"] == "New Task"
            assert result["user_id"] == 1
            assert result["status"] == "todo"
            assert "id" in result

    @pytest.mark.asyncio
    async def test_create_task_with_title_only(self):
        """Should create task with title only."""
        with (
            patch("app.services.task_service.tasks_db", {}),
            patch("app.services.task_service.task_id_counter", {"id": 1}),
            patch("app.services.task_service.datetime"),
        ):
            task_create = TaskCreate(title="Simple Task")
            result = await create_task_service(task_create, 1)

            assert result["title"] == "Simple Task"
            assert result["description"] is None
            assert result["status"] == "todo"

    @pytest.mark.asyncio
    async def test_create_task_increments_id(self):
        """Should increment task ID."""
        mock_counter = {"id": 10}

        with (
            patch("app.services.task_service.tasks_db", {}),
            patch("app.services.task_service.task_id_counter", mock_counter),
            patch("app.services.task_service.datetime"),
        ):
            task_create = TaskCreate(title="Task")
            await create_task_service(task_create, 1)

            assert mock_counter["id"] == 11


class TestGetUserTasksFilteredService:
    """Test get_user_tasks_filtered_service function."""

    @pytest.mark.asyncio
    async def test_get_tasks_empty(self):
        """Should return empty list when no tasks exist."""
        with patch("app.services.task_service.tasks_db", {}):
            result = await get_user_tasks_filtered_service(1)

            assert result["data"] == []
            assert result["pagination"]["total"] == 0

    @pytest.mark.asyncio
    async def test_get_all_user_tasks(self):
        """Should return all tasks for user."""
        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Task 1",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            2: {
                "id": 2,
                "user_id": 1,
                "title": "Task 2",
                "status": "in_progress",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            3: {
                "id": 3,
                "user_id": 2,  # Different user
                "title": "Task 3",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        }

        with patch("app.services.task_service.tasks_db", mock_tasks_db):
            result = await get_user_tasks_filtered_service(1)

            assert len(result["data"]) == 2
            assert all(task["user_id"] == 1 for task in result["data"])

    @pytest.mark.asyncio
    async def test_get_tasks_filter_by_status(self):
        """Should filter tasks by status."""
        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Task 1",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            2: {
                "id": 2,
                "user_id": 1,
                "title": "Task 2",
                "status": "in_progress",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        }

        with patch("app.services.task_service.tasks_db", mock_tasks_db):
            result = await get_user_tasks_filtered_service(
                1,
                status_filter="todo",
            )

            assert len(result["data"]) == 1
            assert result["data"][0]["status"] == "todo"

    @pytest.mark.asyncio
    async def test_get_tasks_search(self):
        """Should search tasks by title."""
        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Learn FastAPI",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            2: {
                "id": 2,
                "user_id": 1,
                "title": "Learn Python",
                "status": "in_progress",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        }

        with patch("app.services.task_service.tasks_db", mock_tasks_db):
            result = await get_user_tasks_filtered_service(1, search="FastAPI")

            # Should find only "Learn FastAPI"
            assert any("FastAPI" in task["title"] for task in result["data"])


class TestUpdateTaskService:
    """Test update_task_service function."""

    @pytest.mark.asyncio
    async def test_update_task_title(self):
        """Should update task title."""
        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Old Title",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        }

        with (
            patch("app.services.task_service.tasks_db", mock_tasks_db),
            patch("app.services.task_service.datetime"),
        ):
            update_data = TaskUpdate(title="New Title")
            result = await update_task_service(1, update_data)

            assert result["title"] == "New Title"
            assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_update_task_not_found(self):
        """Should raise error if task not found."""
        with patch("app.services.task_service.tasks_db", {}):
            update_data = TaskUpdate(title="New Title")

            with pytest.raises(KeyError):
                await update_task_service(999, update_data)

    @pytest.mark.asyncio
    async def test_update_task_not_owner(self):
        """Note: update_task_service doesn't check user ownership, that's done in route handler."""
        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Task",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        }

        with patch("app.services.task_service.tasks_db", mock_tasks_db):
            update_data = TaskUpdate(title="New Title")
            # The service function doesn't validate user ownership, just task existence
            result = await update_task_service(1, update_data)
            assert result["title"] == "New Title"

    @pytest.mark.asyncio
    async def test_update_task_status(self):
        """Should update task status."""
        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Task",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        }

        with (
            patch("app.services.task_service.tasks_db", mock_tasks_db),
            patch("app.services.task_service.datetime"),
        ):
            update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
            result = await update_task_service(1, update_data)

            assert result["status"] == "in_progress"


class TestDeleteTaskService:
    """Test delete_task_service function."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self):
        """Should delete task successfully."""
        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Task",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        }

        with patch("app.services.task_service.tasks_db", mock_tasks_db):
            await delete_task_service(1)

            assert 1 not in mock_tasks_db

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self):
        """Should raise error if task not found."""
        with patch("app.services.task_service.tasks_db", {}):
            with pytest.raises(KeyError):
                await delete_task_service(999)

    @pytest.mark.asyncio
    async def test_delete_task_user_ownership_check_in_handler(self):
        """Note: delete_task_service doesn't check user ownership, that's done in route handler."""
        # This is just testing the service logic, authorization happens at route level
        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Task",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        }

        with patch("app.services.task_service.tasks_db", mock_tasks_db):
            # Service doesn't verify user_id, just deletes by task_id
            await delete_task_service(1)
            assert 1 not in mock_tasks_db
