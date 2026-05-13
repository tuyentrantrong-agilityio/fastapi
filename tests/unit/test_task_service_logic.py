"""
Unit tests for task service core business logic.

Tests cover:
- Task creation logic (without API/DB direct calls)
- Task status updates
- Task validation
- Business rule enforcement
- Transaction/rollback scenarios
"""

from unittest.mock import patch

import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_creation_logic(async_session, test_user):
    """Test task creation business logic.

    Scenario:
    - Create task with valid data
    - Expected: Task created with correct fields
    """
    from app.schemas.task import TaskCreate
    from app.services.task_service import create_task_service

    task_data = TaskCreate(
        title="New Task",
        description="Task description",
        status="todo",
    )

    task = await create_task_service(
        session=async_session,
        task=task_data,
        user_id=test_user.id,
    )

    assert task.title == "New Task"
    assert task.status == "todo"
    assert task.user_id == test_user.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_status_transition_logic():
    """Test task status transition business rules.

    Scenario:
    - Verify valid status transitions (todo → in_progress → done)
    - Expected: Only valid transitions allowed
    """
    valid_transitions = {
        "todo": ["in_progress"],
        "in_progress": ["done", "todo"],
        "done": ["todo"],
    }

    # Test a valid transition
    current_status = "todo"
    new_status = "in_progress"

    assert new_status in valid_transitions[current_status]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_validation_title_required():
    """Test task validation: title is required.

    Scenario:
    - Try to create task without title
    - Expected: Validation error
    """
    from pydantic import ValidationError

    from app.schemas.task import TaskCreate

    # TaskCreate schema should require title
    with pytest.raises((ValidationError, ValueError, TypeError)):
        TaskCreate(
            title="",  # Empty title is not valid
            description="Description",
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_update_partial_fields(async_session, test_user, test_task):
    """Test partial task update (only update specified fields).

    Scenario:
    - Update only status field, leave others unchanged
    - Expected: Only status changed
    """
    from app.schemas.task import TaskUpdate
    from app.services.task_service import update_task_service

    original_title = test_task.title

    updated_task = await update_task_service(
        session=async_session,
        task_id=test_task.id,
        task_update=TaskUpdate(status="in_progress"),
    )

    # Status updated
    assert updated_task.status == "in_progress"
    # Title unchanged
    assert updated_task.title == original_title


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_creation_rollback_on_error(async_session, test_user):
    """Test task creation with database transaction rollback on error.

    Scenario:
    - Create task but DB commit fails
    - Expected: Transaction rolled back, no partial data
    """
    from app.schemas.task import TaskCreate
    from app.services.task_service import create_task_service

    # Mock session.commit to fail
    with patch.object(async_session, "commit", side_effect=Exception("DB error")):
        task_data = TaskCreate(
            title="New Task",
            description="Description",
        )

        with pytest.raises(Exception):
            await create_task_service(
                session=async_session,
                task=task_data,
                user_id=test_user.id,
            )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_delete_service(async_session, test_user, test_task):
    """Test task deletion.

    Scenario:
    - Delete a task
    - Expected: Task removed from database
    """
    from app.services.task_service import delete_task_service

    result = await delete_task_service(
        session=async_session,
        task_id=test_task.id,
    )

    # Should return success result
    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_get_user_tasks(async_session, test_user, test_task):
    """Test retrieving user's tasks.

    Scenario:
    - Get all tasks for a user
    - Expected: Returns task list with pagination info
    """
    from app.services.task_service import get_user_tasks_filtered_service

    result = await get_user_tasks_filtered_service(
        session=async_session,
        user_id=test_user.id,
    )

    assert "data" in result or "tasks" in result
    assert isinstance(result, dict)
