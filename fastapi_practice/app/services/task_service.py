"""Task service - handles task business logic."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import math

from ..schemas.task import TaskCreate, TaskUpdate
from ..schemas.query import SortDirection
from ..core.exceptions import BadRequestException, NotFoundException
from sqlmodel import Session, select
from sqlalchemy import or_, func
from ..models.task import Task


async def create_task_service(session: Session, task: TaskCreate, user_id: int) -> Task:
    """
    Create a new task for user.

    Args:
        task: TaskCreate object
        user_id: ID of the user creating the task

    Returns:
        Created task object
    """
    new_task = Task(**task.__dict__)
    # Set user_id from parameter (not included in TaskCreate schema)
    new_task.user_id = user_id
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task


async def get_user_tasks_filtered_service(
    session: Session,
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

    if page < 1 or limit < 1:
        raise BadRequestException("page and limit must be greater than 0")

    # Helper function to apply filters
    def apply_filters(stmt):
        """Apply status and search filters to statement"""
        # Filter by status (comma-separated values)
        if status_filter:
            status_list = [s.strip() for s in status_filter.split(",") if s.strip()]
            if status_list:
                stmt = stmt.where(Task.status in status_list)
                # stmt = stmt.where(Task.status.in_(status_list))

        # Filter by search (case-insensitive LIKE on title/description)
        if search:
            search_field_list = [f.strip() for f in sort_fields.split(",") if f.strip()]
            conditions = []
            if "title" in search_field_list:
                conditions.append(getattr(Task, "title").ilike(f"%{search}%"))
            if "description" in search_field_list:
                conditions.append(getattr(Task, "description").ilike(f"%{search}%"))
            if conditions:
                stmt = stmt.where(or_(*conditions))

        return stmt

    # Base query for current user
    statement = select(Task).where(Task.user_id == user_id)

    # Apply filters
    statement = apply_filters(statement)

    # Sort by field (asc/desc)
    sort_dir = (
        sort_direction.value
        if sort_direction and hasattr(sort_direction, "value")
        else sort_direction
    )
    reverse = sort_dir == "desc"
    # Whitelist valid fields to prevent injection
    valid_fields = ["title", "description", "status", "created_at", "updated_at"]
    if sort_by not in valid_fields:
        sort_by = "created_at"
    sort_column = getattr(Task, sort_by)
    if reverse:
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column)

    # Pagination - count filtered results efficiently
    count_stmt = (
        select(func.count(Task.id)).select_from(Task).where(Task.user_id == user_id)
    )
    count_stmt = apply_filters(count_stmt)
    total = session.exec(count_stmt).one()

    offset = (page - 1) * limit
    statement = statement.offset(offset).limit(limit)
    items = session.exec(statement).all()
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


async def update_task_service(
    session: Session, task_id: int, task_update: TaskUpdate
) -> Task:
    """
    Update a task.

    Args:
        task_id: ID of the task to update
        task_update: TaskUpdate object with fields to update

    Returns:
        Updated task object
    """
    # Fetch task from database
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    if not task:
        raise NotFoundException("Task not found")

    # Update task fields if provided
    if task_update.title is not None:
        task.title = task_update.title

    if task_update.description is not None:
        task.description = task_update.description

    if task_update.status is not None:
        task.status = (
            task_update.status.value
            if hasattr(task_update.status, "value")
            else task_update.status
        )
    # TODO: Need to improve project

    # Update timestamp and persist changes
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


async def delete_task_service(session: Session, task_id: int) -> dict:
    """
    Delete a task.

    Args:
        task_id: ID of the task to delete

    Returns:
        Dictionary with deleted task id and success message
    """
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    if not task:
        raise NotFoundException("Task not found")

    # Delete task from database
    session.delete(task)
    session.commit()
    return {"id": task_id, "message": "Task deleted successfully"}
