from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_async_session
from ...dependencies.user import get_current_user
from ...schemas.project import ProjectCreate, ProjectResponse
from ...schemas.task import TaskResponse
from ...schemas.user import UserInDB
from ...services.project_service import (
    assign_task_to_project_service,
    create_project_service,
    get_user_projects_service,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Create a new project for current user.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Args:
        project: ProjectCreate object containing name and optional description
        current_user: Current authenticated user (auto-injected)

    Returns:
        Created project with id, user_id, timestamps, etc.
    """
    return await create_project_service(session, project, current_user.id)


@router.get("/", response_model=List[ProjectResponse])
async def get_all_projects(
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get all projects belonging to current user.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Returns:
        List of ProjectResponse objects for current user
    """
    return await get_user_projects_service(session, current_user.id)


@router.post("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def assign_task_to_project(
    project_id: int,
    task_id: int,
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Assign a task to this project.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)
        - User must own both the task and the project

    Args:
        project_id: ID of the project (path parameter)
        task_id: ID of the task to assign (path parameter)

    Returns:
        Updated TaskResponse with project_id set

    Raises:
        404 Not Found: If task or project doesn't exist
        403 Forbidden: If user is not the owner of task or project
    """
    return await assign_task_to_project_service(session, project_id, task_id, current_user.id)
