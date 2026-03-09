from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import math

from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from schemas.user import UserInDB
from schemas.query import TaskFilterParams, SortDirection
from core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from dependencies.user import get_current_user
from dependencies.task import get_task_or_404
from db.storage import tasks_db, task_id_counter, projects_db

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
    task_id = task_id_counter["id"]
    task_id_counter["id"] += 1

    now = datetime.now(timezone.utc)

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


@router.get("/", response_model=Dict[str, Any])
async def get_all_tasks(
    current_user: UserInDB = Depends(get_current_user),
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by status (comma-separated: todo,in_progress,done)",
        examples=["todo,in_progress"],
    ),
    search: Optional[str] = Query(
        None,
        description="Search in title and description (case-insensitive)",
        examples=["documentation"],
    ),
    search_fields: Optional[str] = Query(
        "title,description",
        description="Fields to search in: title, description, or both",
    ),
    sort_by: Optional[str] = Query(
        "created_at",
        description="Sort by: created_at, title, status, updated_at",
    ),
    sort_direction: Optional[SortDirection] = Query(
        "desc",
        description="Sort direction: asc or desc",
    ),
    page: Optional[int] = Query(1, ge=1, description="Page number (1-based)"),
    limit: Optional[int] = Query(
        10, ge=1, le=100, description="Items per page (max 100)"
    ),
):
    """
    Get all tasks belonging to current user with advanced filtering, search, sorting, and pagination.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Query Parameters:
        - **status**: Filter by task status (comma-separated for multiple)
          - Example: `?status=todo` or `?status=todo,in_progress`
        - **search**: Search in title and description (case-insensitive)
          - Example: `?search=documentation`
        - **search_fields**: Fields to search in (default: title,description)
          - Options: title, description, or both
        - **sort_by**: Sort by field (default: created_at)
          - Options: created_at, title, status, updated_at
        - **sort_direction**: Sort direction (default: desc)
          - Options: asc, desc
        - **page**: Page number for pagination (default: 1)
        - **limit**: Items per page, max 100 (default: 10)

    Returns:
        {
            "data": [TaskResponse, ...],
            "pagination": {
                "total": 25,
                "page": 1,
                "limit": 10,
                "pages": 3,
                "has_more": true
            }
        }

    Examples:
        - GET /tasks/ - Get all user's tasks
        - GET /tasks/?status=in_progress - Get active tasks
        - GET /tasks/?search=documentation - Search tasks
        - GET /tasks/?status=done&sort_by=updated_at&sort_direction=asc - Completed tasks, sorted
        - GET /tasks/?search=bug&page=2&limit=5 - Paginated search results
    """
    try:
        filter_params = TaskFilterParams(
            status=status_filter,
            search=search,
            search_fields=search_fields,
            sort_by=sort_by,
            sort_direction=sort_direction,
            page=page,
            limit=limit,
        )
    except ValueError as e:
        raise BadRequestException(str(e))

    # Get all tasks for current user
    user_tasks = [
        task for task in tasks_db.values() if task["user_id"] == current_user.id
    ]

    # Filter by status (Task 19)
    if filter_params.status:
        status_list = [s.strip() for s in filter_params.status.split(",")]
        user_tasks = [task for task in user_tasks if task["status"] in status_list]

    # Search (Task 20)
    if filter_params.search:
        search_lower = filter_params.search.lower()
        search_field_list = [
            f.strip()
            for f in (filter_params.search_fields or "title,description").split(",")
        ]

        filtered = []
        for task in user_tasks:
            match = False
            if "title" in search_field_list and search_lower in task["title"].lower():
                match = True
            if "description" in search_field_list and task.get("description"):
                if search_lower in task["description"].lower():
                    match = True
            if match:
                filtered.append(task)
        user_tasks = filtered

    # Sort
    sort_dir = (
        filter_params.sort_direction.value
        if hasattr(filter_params.sort_direction, "value")
        else filter_params.sort_direction
    )
    try:
        user_tasks.sort(
            key=lambda x: x.get(filter_params.sort_by, ""),
            reverse=(sort_dir == "desc"),
        )
    except (KeyError, TypeError):
        user_tasks.sort(
            key=lambda x: x.get("created_at", datetime.now(timezone.utc)),
            reverse=(sort_dir == "desc"),
        )

    # Pagination
    total = len(user_tasks)
    page = filter_params.page if filter_params.page is not None else 1
    limit = filter_params.limit if filter_params.limit is not None else 10
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
        content={"message": f"Task {task_id} deleted"},
    )


@router.post("/{task_id}/project/{project_id}", response_model=TaskResponse)
async def assign_task_to_project(
    task_id: int,
    project_id: int,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Assign task to project.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own both the task and the project

    Args:
        task_id: ID of the task to assign (path parameter)
        project_id: ID of the project to assign to (path parameter)

    Returns:
        Updated TaskResponse with project_id set

    Raises:
        404 Not Found: If task or project doesn't exist
        403 Forbidden: If user is not the owner of task or project
    """
    # Verify task exists and user owns it
    task = tasks_db.get(task_id)
    if not task:
        raise NotFoundException("Task", task_id)
    if task["user_id"] != current_user.id:
        raise ForbiddenException("You don't have permission to access this task")

    # Verify project exists and user owns it
    project = projects_db.get(project_id)
    if not project:
        raise NotFoundException("Project", project_id)
    if project["user_id"] != current_user.id:
        raise ForbiddenException("You don't have permission to access this project")

    # Assign task to project
    task["project_id"] = project_id
    task["updated_at"] = datetime.now(timezone.utc)

    return task
