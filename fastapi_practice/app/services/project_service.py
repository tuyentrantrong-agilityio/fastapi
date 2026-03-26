"""Project service - handles project business logic."""

from datetime import datetime, timezone
from typing import List

from ..core.exceptions import NotFoundException, ForbiddenException
from sqlmodel import Session, select
from ..models.project import Project
from ..models.task import Task
from ..schemas.project import ProjectCreate


async def create_project_service(
    session: Session, project: ProjectCreate, user_id: int
) -> Project:
    """
    Create a new project for user.

    Args:
        project: ProjectCreate object
        user_id: ID of the user creating the project

    Returns:
        Created project object
    """
    new_project = Project(**project.__dict__)
    # Set user_id from parameter (not included in ProjectCreate schema)
    new_project.user_id = user_id
    session.add(new_project)
    session.commit()
    session.refresh(new_project)

    return new_project


async def get_user_projects_service(session: Session, user_id: int) -> List[Project]:
    """
    Get all projects for a user.

    Args:
        user_id: ID of the user

    Returns:
        List of project objects
    """
    # Query database for all projects owned by user
    statement = select(Project).where(Project.user_id == user_id)
    user_projects = session.exec(statement).all()
    # Convert Sequence to List for consistency
    return list(user_projects)


async def assign_task_to_project_service(
    session: Session, project_id: int, task_id: int, user_id: int
) -> Task:
    """
    Assign a task to a project.

    Args:
        project_id: ID of the project
        task_id: ID of the task
        user_id: ID of the user (must own both project and task)

    Returns:
        Updated task object

    Raises:
        NotFoundException: If project or task not found
        ForbiddenException: If user doesn't own the project or task
    """
    # Verify project exists and user has permission
    statement = select(Project).where(Project.id == project_id)
    project = session.exec(statement).first()
    if not project:
        raise NotFoundException("Project", project_id)
    if project.user_id != user_id:
        raise ForbiddenException("You don't have permission to access this project")

    # Verify task exists and user has permission
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    if not task:
        raise NotFoundException("Task", task_id)
    if task.user_id != user_id:
        raise ForbiddenException("You don't have permission to access this task")

    # Assign task to project with updated timestamp
    task.project_id = project_id
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)

    return task
