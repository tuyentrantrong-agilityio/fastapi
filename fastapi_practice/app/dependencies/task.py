from fastapi import Depends
from typing import Dict, Any

from ..schemas.user import UserInDB
from ..core.exceptions import NotFoundException, ForbiddenException
from ..dependencies.user import get_current_user
from ..db.storage import tasks_db


async def get_task_or_404(
    task_id: int, current_user: UserInDB = Depends(get_current_user)
) -> Dict[str, Any]:
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
    task = tasks_db.get(task_id)

    if not task:
        raise NotFoundException("Task", task_id)

    # Verify ownership
    if task["user_id"] != current_user.id:
        raise ForbiddenException("You don't have permission to access this task")

    return task
