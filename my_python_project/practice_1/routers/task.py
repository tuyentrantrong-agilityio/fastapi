from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List

from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatus
from schemas.user import UserInDB
from dependencies.user import get_current_user
from dependencies.task import get_task_or_404
from db.storage import tasks_db, task_id_counter

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate, current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new task for current user.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Args:
        task: TaskCreate object containing title, description (optional), and status (default: todo)
        current_user: Current authenticated user (auto-injected)

    Returns:
        Created task with id, user_id, timestamps, etc.
    """
    # Create new task
    task_id = task_id_counter["id"]
    task_id_counter["id"] += 1

    now = datetime.utcnow()

    tasks_db[task_id] = {
        "id": task_id,
        "user_id": current_user.id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value if hasattr(task.status, "value") else task.status,
        "created_at": now,
        "updated_at": now,
    }

    return tasks_db[task_id]


@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks(current_user: UserInDB = Depends(get_current_user)):
    """
    Get all tasks belonging to current user.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Returns:
        List of TaskResponse objects for current user
    """
    user_tasks = [
        task for task in tasks_db.values() if task["user_id"] == current_user.id
    ]
    return user_tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task: dict = Depends(get_task_or_404),
):
    """
    Get task by ID.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own the task

    Args:
        task_id: ID of the task to retrieve (path parameter)

    Returns:
        TaskResponse object

    Raises:
        404 Not Found: If task doesn't exist
        403 Forbidden: If user is not the task owner
    """
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    task: dict = Depends(get_task_or_404),
):
    """
    Update task by ID.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own the task

    Args:
        task_id: ID of the task to update (path parameter)
        task_update: TaskUpdate object with fields to update

    Returns:
        Updated TaskResponse object

    Raises:
        404 Not Found: If task doesn't exist
        403 Forbidden: If user is not the task owner
    """
    # Update fields
    if task_update.title is not None:
        task["title"] = task_update.title

    if task_update.description is not None:
        task["description"] = task_update.description

    if task_update.status is not None:
        task["status"] = (
            task_update.status.value
            if hasattr(task_update.status, "value")
            else task_update.status
        )

    # Update timestamp
    task["updated_at"] = datetime.utcnow()

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    task: dict = Depends(get_task_or_404),
):
    """
    Delete task by ID.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own the task

    Args:
        task_id: ID of the task to delete (path parameter)

    Returns:
        Success message

    Raises:
        404 Not Found: If task doesn't exist
        403 Forbidden: If user is not the task owner
    """
    del tasks_db[task_id]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Task {task_id} deleted successfully"},
    )
