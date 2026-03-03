from fastapi import APIRouter, status, Depends
from datetime import datetime

from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatus
from schemas.user import UserInDB
from dependencies.user import get_current_user
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
