"""Task service - handles task business logic."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import math

from ..schemas.task import TaskCreate, TaskUpdate
from ..schemas.query import SortDirection
from ..core.exceptions import BadRequestException
from ..db.storage import tasks_db, task_id_counter


async def create_task_service(task: TaskCreate, user_id: int) -> dict:
    """
    Create a new task for user.

    Args:
        task: TaskCreate object
        user_id: ID of the user creating the task

    Returns:
        Created task dictionary
    """
    task_id = task_id_counter["id"]
    task_id_counter["id"] += 1

    now = datetime.now(timezone.utc)

    tasks_db[task_id] = {
        "id": task_id,
        "user_id": user_id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value if hasattr(task.status, "value") else task.status,
        "created_at": now,
        "updated_at": now,
    }

    return tasks_db[task_id]


async def get_user_tasks_filtered_service(
    user_id: int,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    search_fields: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[SortDirection] = None,
    page: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get user's tasks with filtering, search, sorting, and pagination.

    Args:
        user_id: ID of the user
        status_filter: Comma-separated status list
        search: Search term
        search_fields: Fields to search in
        sort_by: Field to sort by
        sort_direction: Sort direction (asc/desc)
        page: Page number (1-based)
        limit: Items per page

    Returns:
        Dictionary with data (tasks) and pagination info

    Raises:
        BadRequestException: If filter params are invalid
    """
    # Defaults
    page = page if page is not None else 1
    limit = limit if limit is not None else 10
    sort_by = sort_by or "created_at"
    sort_fields = search_fields or "title,description"

    # Get all tasks for current user
    user_tasks = [task for task in tasks_db.values() if task["user_id"] == user_id]

    # Filter by status
    if status_filter:
        status_list = [s.strip() for s in status_filter.split(",")]
        user_tasks = [task for task in user_tasks if task["status"] in status_list]

    # Search
    if search:
        search_lower = search.lower()
        search_field_list = [f.strip() for f in sort_fields.split(",")]

        filtered = []
        for task in user_tasks:
            match = False
            if "title" in search_field_list and search_lower in task["title"].lower():
                match = True
            if (
                "description" in search_field_list
                and task.get("description")
                and search_lower in task["description"].lower()
            ):
                match = True
            if match:
                filtered.append(task)
        user_tasks = filtered

    # Sort
    sort_dir = (
        sort_direction.value
        if sort_direction and hasattr(sort_direction, "value")
        else sort_direction
    )
    try:
        user_tasks.sort(
            key=lambda x: x.get(sort_by, ""),
            reverse=(sort_dir == "desc"),
        )
    except (KeyError, TypeError):
        user_tasks.sort(
            key=lambda x: x.get("created_at", datetime.now(timezone.utc)),
            reverse=(sort_dir == "desc"),
        )

    # Pagination
    total = len(user_tasks)
    offset = (page - 1) * limit
    items = user_tasks[offset : offset + limit]
    pages = math.ceil(total / limit) if total > 0 else 1

    return {
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
            "has_more": page < pages,
        },
    }


async def update_task_service(task_id: int, task_update: TaskUpdate) -> dict:
    """
    Update a task.

    Args:
        task_id: ID of the task to update
        task_update: TaskUpdate object with fields to update

    Returns:
        Updated task dictionary
    """
    task = tasks_db[task_id]

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

    task["updated_at"] = datetime.now(timezone.utc)
    return task


async def delete_task_service(task_id: int) -> dict:
    """
    Delete a task.

    Args:
        task_id: ID of the task to delete

    Returns:
        Deleted task dictionary
    """
    task = tasks_db.pop(task_id)
    return task
