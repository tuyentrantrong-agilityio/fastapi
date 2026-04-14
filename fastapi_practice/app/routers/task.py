from fastapi import APIRouter, status, Depends, Query, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..schemas.user import UserInDB
from ..schemas.query import TaskFilterParams, SortDirection
from ..core.exceptions import BadRequestException
from ..core.cache_keys import task_list_cache_key, TASK_LIST_CACHE_TTL
from ..core.websocket_manager import manager
from ..dependencies.user import get_current_user
from ..dependencies.task import get_owned_task_or_error
from ..dependencies.cache import get_cache
from ..db.session import get_async_session
from ..services.task_service import (
    create_task_service,
    get_user_tasks_filtered_service,
    update_task_service,
    delete_task_service,
)
from ..services.cache_service import CacheService
from ..tasks.email_tasks import send_task_assigned_email_task
from ..tasks.task_tasks import process_task_async
from ..tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    cache: CacheService = Depends(get_cache),
):
    """
    Create a new task for current user and send assignment email via Celery.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Args:
        task: TaskCreate object containing title, description (optional), and status (default: todo)
        current_user: Current authenticated user (auto-injected)
        session: Database session (auto-injected)
        cache: Cache service (auto-injected)

    Returns:
        Created task with id, user_id, timestamps, etc.
    """
    new_task = await create_task_service(session, task, current_user.id)

    # Invalidate task list cache for this user
    await cache.delete_pattern(f"tasks:u{current_user.id}:*")
    logger.info(f"Cache invalidated for user {current_user.id} after task creation")

    # Queue email task via Celery
    send_task_assigned_email_task.delay(
        email=current_user.email,
        user_name=current_user.email.split("@")[0],
        task_title=new_task.title,
        task_id=new_task.id if new_task.id is not None else 0,
        assigned_by="You",
    )
    return new_task


@router.get("/", response_model=Dict[str, Any])
async def get_all_tasks(
    response: Response,
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    cache: CacheService = Depends(get_cache),
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

    # Generate cache key
    cache_key = task_list_cache_key(
        user_id=current_user.id,
        status=filter_params.status,
        search=filter_params.search,
        page=filter_params.page
    )
    
    # Try to get from cache first
    cached_result = await cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache HIT for user {current_user.id} tasks list")
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-Key"] = cache_key
        return cached_result
    
    logger.info(f"Cache MISS for user {current_user.id} tasks list, fetching from DB")
    response.headers["X-Cache"] = "MISS"
    response.headers["X-Cache-Key"] = cache_key
    
    # Fetch from database
    result = await get_user_tasks_filtered_service(
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

    # SQLAlchemy/SQLModel objects and datetimes must be JSON-compatible for Redis cache.
    result_json = jsonable_encoder(result)
    
    # Store in cache with TTL
    cache_saved = await cache.set(cache_key, result_json, ttl=TASK_LIST_CACHE_TTL)
    response.headers["X-Cache-Store"] = "OK" if cache_saved else "ERROR"
    
    return result_json


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
    current_user: UserInDB = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
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
        current_user: Current authenticated user (auto-injected)
        cache: Cache service (auto-injected)

    Returns:
        Updated TaskResponse object

    Raises:
        404 Not Found: If task doesn't exist
        403 Forbidden: If user is not the task owner
    """
    result = await update_task_service(session, task_id, task_update)
    
    # Invalidate cache for this user's task list
    await cache.delete_pattern(f"tasks:u{current_user.id}:*")
    logger.info(f"Cache invalidated for user {current_user.id} after task update")
    
    # [KEY] NEW: Broadcast to all subscribed WebSocket clients
    try:
        await manager.broadcast_to_subscribers(
            task_id=result.id,
            message={
                "event": "task_updated",
                "task_id": result.id,
                "status": result.status,
                "title": result.title,
                "description": result.description,
                "updated_at": result.updated_at.isoformat() if result.updated_at else None,
                "user_id": result.user_id
            }
        )
        logger.info(f"WebSocket notification sent for task {task_id} update")
    except Exception as e:
        # WebSocket broadcast failure should NOT crash the update endpoint
        # Task is already updated in DB, just real-time notification failed
        logger.error(f"WebSocket broadcast failed for task {task_id}: {e}", exc_info=True)
    
    return result


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    task: dict = Depends(get_owned_task_or_error),
    session: AsyncSession = Depends(get_async_session),
    current_user: UserInDB = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
):
    """
    Delete task by ID.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own the task

    Args:
        task_id: ID of the task to delete (path parameter)
        session: Database session (auto-injected)
        current_user: Current authenticated user (auto-injected)
        cache: Cache service (auto-injected)

    Returns:
        Success message

    Raises:
        404 Not Found: If task doesn't exist
        403 Forbidden: If user is not the task owner
    """
    await delete_task_service(session, task_id)
    
    # Invalidate cache for this user's task list
    await cache.delete_pattern(f"tasks:u{current_user.id}:*")
    logger.info(f"Cache invalidated for user {current_user.id} after task deletion")
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Task {task_id} deleted"},
    )


@router.post("/{task_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_task(
    task_id: int,
    task: dict = Depends(get_owned_task_or_error),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Trigger async task processing (long-running operation).

    Workflow:
    1. Endpoint accepts request, triggers Celery task immediately
    2. Returns task ID for client to poll status
    3. Celery worker processes task in background (delay 5-10s)
    4. Task status: todo -> in_progress -> done
    5. Client polls GET /tasks/{task_id}/status to track progress

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own the task
        - Task status must be "todo"

    Args:
        task_id: ID of the task to process (path parameter)
        current_user: Current authenticated user (auto-injected)

    Returns:
        {
            "celery_task_id": "abc123def456",  # Use to poll status
            "status": "accepted",
            "message": "Task processing started, check /tasks/{task_id}/status",
            "task_id": 1
        }

    Raises:
        404 Not Found: If task doesn't exist
        403 Forbidden: If user is not the task owner

    Example:
        1. POST /tasks/1/process -> returns {"celery_task_id": "abc123", ...}
        2. Poll: GET /tasks/1/status -> {"status": "in_progress"}
        3. Wait 5-10s...
        4. Poll: GET /tasks/1/status -> {"status": "done"}
    """
    # Trigger Celery task (returns immediately with task ID)
    celery_task = process_task_async.delay(task_id)
    
    return {
        "celery_task_id": celery_task.id,
        "status": "accepted",
        "message": "Task processing started, check /tasks/{}/status".format(task_id),
        "task_id": task_id
    }


@router.get("/{task_id}/status")
async def get_task_status(
    task_id: int,
    task: dict = Depends(get_owned_task_or_error),
):
    """
    Check task processing status and current task status in database.

    Use this endpoint to poll task progress after triggering POST /tasks/{task_id}/process

    Returns:
        {
            "task_id": 1,
            "task_status": "in_progress",  # Database: todo, in_progress, done
            "celery_status": "PROGRESS"     # Celery: PENDING, PROGRESS, SUCCESS, FAILURE
        }

    Example polling flow:
        1. POST /tasks/1/process
        2. Loop: GET /tasks/1/status until task_status == "done"
        3. Render final result to user

    Returns:
        Task current status from database
    """
    # Convert SQLModel to dict for response
    task_dict = {
        "task_id": task_id,
        "task_status": task.status if task else "unknown",
        "message": "Check this endpoint until task_status becomes 'done'"
    }
    return task_dict
