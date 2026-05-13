from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..core.exceptions import ForbiddenException, NotFoundException
from ..db.session import get_async_session
from ..dependencies.user import get_current_user
from ..models.task import Task
from ..schemas.user import UserInDB


async def get_owned_task_or_error(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserInDB = Depends(get_current_user),
) -> Task:
    """
    Get task by ID and verify current user owns it.

    Args:
        task_id: ID of the task to retrieve
        session: AsyncSession for database operations
        current_user: Current authenticated user (auto-injected)

    Returns:
        Task data

    Raises:
        NotFoundException: If task not found (404)
        ForbiddenException: If user is not the task owner (403)
    """
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    task = result.scalars().first()

    if not task:
        # Task not found => Raise 404 NotFound
        raise NotFoundException("Task", task_id)

    # Verify ownership
    if task.user_id != current_user.id:
        # User is not the owner => Raise 403 Forbidden
        raise ForbiddenException("You don't have permission to access this task")

    return task
