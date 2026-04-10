from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..schemas.user import UserInDB
from ..schemas.query import TaskFilterParams, SortDirection
from ..core.exceptions import BadRequestException
from ..dependencies.user import get_current_user
from ..dependencies.task import get_owned_task_or_error
from ..db.session import get_async_session
from ..services.task_service import (
    create_task_service,
    get_user_tasks_filtered_service,
    update_task_service,
    delete_task_service,
)
from ..tasks.email_tasks import send_task_assigned_email_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Create a new task for current user and send assignment email via Celery.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Args:
        task: TaskCreate object containing title, description (optional), and status (default: todo)
        current_user: Current authenticated user (auto-injected)
        session: Database session (auto-injected)

    Returns:
        Created task with id, user_id, timestamps, etc.
    """
    new_task = await create_task_service(session, task, current_user.id)
    
    # Queue email task via Celery
    send_task_assigned_email_task.delay(
        email=current_user.email,
        user_name=current_user.email.split("@")[0],
        task_title=new_task.title,
        task_id=new_task.id if new_task.id is not None else 0,
        assigned_by="You"
    )
    return new_task


@router.get("/", response_model=Dict[str, Any])
async def get_all_tasks(
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
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

    return await get_user_tasks_filtered_service(
        session=session,
        user_id=current_user.id,
        status_filter=filter_params.status,
        search=filter_params.search,
        search_fields=filter_params.search_fields,
        sort_by=filter_params.sort_by,
        sort_direction=filter_params.sort_direction,
        page=filter_params.page,
        limit=filter_params.limit,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    task: dict = Depends(get_owned_task_or_error),
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
    task: dict = Depends(get_owned_task_or_error),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Update task by ID.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own the task

    Args:
        task_id: ID of the task to update (path parameter)
        task_update: TaskUpdate object with fields to update
        session: Database session (auto-injected)

    Returns:
        Updated TaskResponse object

    Raises:
        404 Not Found: If task doesn't exist
        403 Forbidden: If user is not the task owner
    """
    return await update_task_service(session, task_id, task_update)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    task: dict = Depends(get_owned_task_or_error),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Delete task by ID.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own the task

    Args:
        task_id: ID of the task to delete (path parameter)
        session: Database session (auto-injected)

    Returns:
        Success message

    Raises:
        404 Not Found: If task doesn't exist
        403 Forbidden: If user is not the task owner
    """
    await delete_task_service(session, task_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Task {task_id} deleted"},
    )
