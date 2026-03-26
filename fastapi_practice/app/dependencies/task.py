from fastapi import Depends
from typing import Dict, Any

from ..schemas.user import UserInDB
from ..core.exceptions import NotFoundException, ForbiddenException
from ..dependencies.user import get_current_user
from sqlmodel import Session, select
from ..models.task import Task


from app.db.session import get_session


async def get_task_or_404(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> Task:
    """
    Get task by ID and verify current user owns it.

    Args:
        task_id: ID of the task to retrieve
        current_user: Current authenticated user (auto-injected)

    Returns:
        Task data dictionary

    Raises:
        NotFoundException: If task not found
        ForbiddenException: If user is not the task owner
    """
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()

    if not task:
        raise NotFoundException("Task", task_id)

    # Verify ownership
    if task.user_id != current_user.id:
        raise ForbiddenException("You don't have permission to access this task")

    return task
