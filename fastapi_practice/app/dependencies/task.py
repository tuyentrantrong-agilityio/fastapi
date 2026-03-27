from fastapi import Depends
from typing import Dict, Any

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.user import UserInDB
from ..core.exceptions import NotFoundException, ForbiddenException
from ..dependencies.user import get_current_user
from ..models.task import Task
from ..db.session import get_async_session


async def get_task_or_404(
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
        NotFoundException: If task not found
        ForbiddenException: If user is not the task owner
    """
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    task = result.scalars().first()

    if not task:
        raise NotFoundException("Task", task_id)

    # Verify ownership
    if task.user_id != current_user.id:
        raise ForbiddenException("You don't have permission to access this task")

    return task
