from fastapi import APIRouter, status, Depends
from datetime import datetime, timezone
from typing import List

from ..schemas.project import ProjectCreate, ProjectResponse
from ..schemas.task import TaskResponse
from ..schemas.user import UserInDB
from ..core.exceptions import NotFoundException, ForbiddenException
from ..dependencies.user import get_current_user
from ..db.storage import projects_db, project_id_counter, tasks_db

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, current_user: UserInDB = Depends(get_current_user)
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
    project_id = project_id_counter["id"]
    project_id_counter["id"] += 1

    now = datetime.now(timezone.utc)

    projects_db[project_id] = {
        "id": project_id,
        "user_id": current_user.id,
        "name": project.name,
        "description": project.description,
        "created_at": now,
        "updated_at": now,
    }

    return projects_db[project_id]


@router.get("/", response_model=List[ProjectResponse])
async def get_all_projects(current_user: UserInDB = Depends(get_current_user)):
    """
    Get all projects belonging to current user.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Returns:
        List of ProjectResponse objects for current user
    """
    user_projects = [
        project
        for project in projects_db.values()
        if project["user_id"] == current_user.id
    ]
    return user_projects


@router.post("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def assign_task_to_project(
    project_id: int,
    task_id: int,
    current_user: UserInDB = Depends(get_current_user),
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
    # Verify project exists and user owns it
    project = projects_db.get(project_id)
    if not project:
        raise NotFoundException("Project", project_id)
    if project["user_id"] != current_user.id:
        raise ForbiddenException("You don't have permission to access this project")

    # Verify task exists and user owns it
    task = tasks_db.get(task_id)
    if not task:
        raise NotFoundException("Task", task_id)
    if task["user_id"] != current_user.id:
        raise ForbiddenException("You don't have permission to access this task")

    # Assign task to project
    task["project_id"] = project_id
    task["updated_at"] = datetime.now(timezone.utc)

    return task
