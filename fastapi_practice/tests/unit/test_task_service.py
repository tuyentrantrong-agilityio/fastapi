"""Unit tests for task service functions with mocked AsyncSession."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.services.task_service import (
    create_task_service,
    update_task_service,
    delete_task_service,
    get_user_tasks_filtered_service,
)
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatus
from app.models.task import Task
from app.core.exceptions import NotFoundException, BadRequestException


def make_task(
    id=1, user_id=1, title="Task", description=None, status="todo", project_id=None
):
    """Helper to create Task model instance."""
    task = Task(
        id=id,
        user_id=user_id,
        title=title,
        description=description,
        status=status,
        project_id=project_id,
    )
    return task


class TestCreateTaskService:
    """Test cases for create_task_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Should successfully create task."""

        # --- Mock session and DB operations ---
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Prepare input DTO ---
        task_create = TaskCreate(
            title="New Task", description="Task Description", status=TaskStatus.TODO
        )

        # --- Mock DB refresh to assign ID ---
        def side_effect_refresh(task):
            task.id = 1

        session.refresh.side_effect = side_effect_refresh

        # --- Call the service function under test ---
        result = await create_task_service(session, task_create, user_id=42)

        # --- Assert task was created with correct values ---
        session.add.assert_called_once()  # Task added to session
        session.commit.assert_awaited_once()  # Changes committed
        session.refresh.assert_awaited_once()  # Task refreshed with DB-assigned ID
        assert result.user_id == 42  # Correct owner
        assert result.title == "New Task"
        assert result.status == "todo"

    @pytest.mark.asyncio
    async def test_with_title_only(self):
        """Should create task with title only."""

        # --- Mock session and DB operations ---
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Prepare minimal input DTO (title only, no description/status) ---
        task_create = TaskCreate(title="Simple Task")

        # --- Call the service function under test ---
        result = await create_task_service(session, task_create, user_id=42)

        # --- Assert task created with defaults ---
        assert result.title == "Simple Task"
        assert result.description is None  # Optional field
        assert result.status == "todo"  # Default status
        session.add.assert_called_once()  # Task added to session


class TestUpdateTaskService:
    """Test cases for update_task_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Should successfully update task."""

        # --- Mock session and existing task in database ---
        session = AsyncMock(spec=AsyncSession)
        existing = make_task(id=7, title="Old", status="todo", user_id=42)
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = (
            existing  # Simulate: task found
        )
        session.execute.return_value = query_result

        # --- Mock DB operations ---
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Prepare input DTO with updates ---
        update_dto = TaskUpdate(title="New", status=TaskStatus.IN_PROGRESS)

        # --- Call the service function under test ---
        updated = await update_task_service(session, task_id=7, task_update=update_dto)

        # --- Assert query and DB operations executed ---
        session.execute.assert_awaited_once()  # Task lookup executed
        session.commit.assert_awaited_once()  # Changes committed
        session.refresh.assert_awaited_once()  # Task refreshed
        assert updated.title == "New"  # Title updated
        assert updated.status == "in_progress"  # Status updated

    @pytest.mark.asyncio
    async def test_not_found(self):
        """Should raise NotFoundException if task not found."""

        # --- Mock session with no task found ---
        session = AsyncMock(spec=AsyncSession)
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = (
            None  # Simulate: task doesn't exist
        )
        session.execute.return_value = query_result

        # --- Call and verify exception is raised ---
        with pytest.raises(NotFoundException):
            await update_task_service(
                session, task_id=99, task_update=TaskUpdate(title="X")
            )

    @pytest.mark.asyncio
    async def test_partial(self):
        """Should support partial updates."""

        # --- Mock session and existing task ---
        session = AsyncMock(spec=AsyncSession)
        existing = make_task(
            id=5, title="Original", description="Original desc", status="todo"
        )
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = existing
        session.execute.return_value = query_result

        # --- Mock DB operations ---
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Prepare partial update (only status changed) ---
        update_dto = TaskUpdate(status=TaskStatus.DONE)

        # --- Call the service function under test ---
        result = await update_task_service(session, task_id=5, task_update=update_dto)

        # --- Assert only specified fields changed, others preserved ---
        assert result.title == "Original"  # Unchanged
        assert result.description == "Original desc"  # Unchanged
        assert result.status == "done"  # Only this changed


class TestDeleteTaskService:
    """Test cases for delete_task_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Should delete task successfully."""

        # --- Mock session and existing task in database ---
        session = AsyncMock(spec=AsyncSession)
        existing = make_task(id=10, title="ToDelete", user_id=42)
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = (
            existing  # Simulate: task found
        )
        session.execute.return_value = query_result

        # --- Mock DB delete operations ---
        session.delete = AsyncMock()
        session.commit = AsyncMock()

        # --- Call the service function under test ---
        result = await delete_task_service(session, task_id=10)

        # --- Assert task was deleted from DB ---
        session.delete.assert_awaited_once_with(existing)  # Correct task deleted
        session.commit.assert_awaited_once()  # Changes committed
        assert result["id"] == 10  # Confirmation response
        assert "deleted" in result["message"].lower()  # Success message

    @pytest.mark.asyncio
    async def test_not_found(self):
        """Should raise NotFoundException if task not found."""

        # --- Mock session with no task found ---
        session = AsyncMock(spec=AsyncSession)
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = (
            None  # Simulate: task doesn't exist
        )
        session.execute.return_value = query_result

        # --- Call and verify exception is raised ---
        with pytest.raises(NotFoundException):
            await delete_task_service(session, task_id=999)


class TestGetUserTasksFilteredService:
    """Test cases for get_user_tasks_filtered_service."""

    @pytest.mark.asyncio
    async def test_empty(self):
        """Should return empty list when no tasks exist."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Mock count query (no tasks) ---
        count_query_result = MagicMock()
        count_query_result.scalar.return_value = 0

        # --- Mock items query (empty result) ---
        items_query_result = MagicMock()
        items_query_result.scalars.return_value.all.return_value = []

        # --- Mock session to return count first, then items ---
        session.execute.side_effect = [count_query_result, items_query_result]

        # --- Call the service function under test ---
        result = await get_user_tasks_filtered_service(session, user_id=42)

        # --- Assert empty result with correct pagination ---
        assert result["data"] == []  # No tasks
        assert result["pagination"]["total"] == 0  # Total count is zero
        assert result["pagination"]["page"] == 1  # Default page

    @pytest.mark.asyncio
    async def test_multiple(self):
        """Should return all tasks for user."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Create task instances ---
        task1 = make_task(id=1, user_id=42, title="Task 1", status="todo")
        task2 = make_task(id=2, user_id=42, title="Task 2", status="in_progress")

        # --- Mock count query (2 total tasks) ---
        count_query_result = MagicMock()
        count_query_result.scalar.return_value = 2

        # --- Mock items query (both tasks returned) ---
        items_query_result = MagicMock()
        items_query_result.scalars.return_value.all.return_value = [task1, task2]

        # --- Mock session to return count first, then items ---
        session.execute.side_effect = [count_query_result, items_query_result]

        # --- Call the service function under test ---
        result = await get_user_tasks_filtered_service(session, user_id=42)

        # --- Assert all tasks returned with correct pagination ---
        assert len(result["data"]) == 2  # Both tasks returned
        assert result["pagination"]["total"] == 2  # Total count correct

    @pytest.mark.asyncio
    async def test_status_filter(self):
        """Should filter tasks by status."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Create task with specific status ---
        task1 = make_task(id=1, user_id=42, title="Task 1", status="todo")

        # --- Mock count query (1 task matches filter) ---
        count_query_result = MagicMock()
        count_query_result.scalar.return_value = 1

        # --- Mock items query (filtered result) ---
        items_query_result = MagicMock()
        items_query_result.scalars.return_value.all.return_value = [task1]

        # --- Mock session to return count first, then items ---
        session.execute.side_effect = [count_query_result, items_query_result]

        # --- Call the service with status filter ---
        result = await get_user_tasks_filtered_service(
            session, user_id=42, status_filter="todo"
        )

        # --- Assert only matching tasks returned ---
        assert len(result["data"]) == 1  # Only 1 task after filter
        assert result["data"][0].status == "todo"  # Correct status

    @pytest.mark.asyncio
    async def test_pagination(self):
        """Should handle pagination correctly."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Create 5 task instances (1 page) ---
        tasks = [make_task(id=i, user_id=42, title=f"Task {i}") for i in range(1, 6)]

        # --- Mock count query (10 total tasks across all pages) ---
        count_query_result = MagicMock()
        count_query_result.scalar.return_value = 10

        # --- Mock items query (5 tasks on page 1) ---
        items_query_result = MagicMock()
        items_query_result.scalars.return_value.all.return_value = tasks

        # --- Mock session to return count first, then items ---
        session.execute.side_effect = [count_query_result, items_query_result]

        # --- Call the service with pagination params (page=1, limit=5) ---
        result = await get_user_tasks_filtered_service(
            session, user_id=42, page=1, limit=5
        )

        # --- Assert pagination metadata correct ---
        assert len(result["data"]) == 5  # 5 items on this page
        assert result["pagination"]["total"] == 10  # 10 total across all pages
        assert result["pagination"]["page"] == 1  # Current page
        assert result["pagination"]["pages"] == 2  # 2 pages total (10 / 5)
        assert result["pagination"]["has_more"] is True  # More pages exist

    @pytest.mark.asyncio
    async def test_search(self):
        """Should search tasks by title."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Create task matching search keyword ---
        task = make_task(
            id=1, user_id=42, title="Learn FastAPI", description="Complete tutorial"
        )

        # --- Mock count query (1 task matches search) ---
        count_query_result = MagicMock()
        count_query_result.scalar.return_value = 1

        # --- Mock items query (search result) ---
        items_query_result = MagicMock()
        items_query_result.scalars.return_value.all.return_value = [task]

        # --- Mock session to return count first, then items ---
        session.execute.side_effect = [count_query_result, items_query_result]

        # --- Call the service with search parameter ---
        result = await get_user_tasks_filtered_service(
            session, user_id=42, search="FastAPI"
        )

        # --- Assert search results correct ---
        assert len(result["data"]) == 1  # Only matching task returned
        assert "FastAPI" in result["data"][0].title  # Search term in result

    @pytest.mark.asyncio
    async def test_bad_pagination(self):
        """Should raise BadRequestException for invalid pagination."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Call with invalid pagination params (page=0, limit=0) ---
        with pytest.raises(BadRequestException):
            await get_user_tasks_filtered_service(session, user_id=42, page=0, limit=0)
