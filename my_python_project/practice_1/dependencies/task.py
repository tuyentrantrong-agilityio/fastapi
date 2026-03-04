from fastapi import Depends, HTTPException, status
from typing import Dict, Any

from schemas.user import UserInDB
from dependencies.user import get_current_user
from db.storage import tasks_db


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
        HTTPException 404: If task not found
        HTTPException 403: If user is not the task owner
    """
    task = tasks_db.get(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Verify ownership
    if task["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task",
        )

    return task
