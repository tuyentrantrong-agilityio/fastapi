"""Project service - handles project business logic."""

from datetime import datetime, timezone
from typing import List

from ..core.exceptions import NotFoundException, ForbiddenException
from ..db.storage import projects_db, project_id_counter, tasks_db
from ..schemas.project import ProjectCreate


async def create_project_service(project: ProjectCreate, user_id: int) -> dict:
    """
    Create a new project for user.

    Args:
        project: ProjectCreate object
        user_id: ID of the user creating the project

    Returns:
        Created project dictionary
    """
    project_id = project_id_counter["id"]
    project_id_counter["id"] += 1

    now = datetime.now(timezone.utc)

    projects_db[project_id] = {
        "id": project_id,
        "user_id": user_id,
        "name": project.name,
        "description": project.description,
        "created_at": now,
        "updated_at": now,
    }

    return projects_db[project_id]


async def get_user_projects_service(user_id: int) -> List[dict]:
    """
    Get all projects for a user.

    Args:
        user_id: ID of the user

    Returns:
        List of project dictionaries
    """
    user_projects = [
        project for project in projects_db.values() if project["user_id"] == user_id
    ]
    return user_projects


async def assign_task_to_project_service(
    project_id: int, task_id: int, user_id: int
) -> dict:
    """
    Assign a task to a project.

    Args:
        project_id: ID of the project
        task_id: ID of the task
        user_id: ID of the user (must own both project and task)

    Returns:
        Updated task dictionary

    Raises:
        NotFoundException: If project or task not found
        ForbiddenException: If user doesn't own the project or task
    """
    # Verify project exists and user owns it
    project = projects_db.get(project_id)
    if not project:
        raise NotFoundException("Project", project_id)
    if project["user_id"] != user_id:
        raise ForbiddenException("You don't have permission to access this project")

    # Verify task exists and user owns it
    task = tasks_db.get(task_id)
    if not task:
        raise NotFoundException("Task", task_id)
    if task["user_id"] != user_id:
        raise ForbiddenException("You don't have permission to access this task")

    # Assign task to project
    task["project_id"] = project_id
    task["updated_at"] = datetime.now(timezone.utc)

    return task
