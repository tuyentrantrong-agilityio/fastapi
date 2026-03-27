"""Project service - handles project business logic."""

from datetime import datetime, timezone
from typing import List

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import NotFoundException, ForbiddenException
from ..models.project import Project
from ..models.task import Task
from ..schemas.project import ProjectCreate


async def create_project_service(
    session: AsyncSession, project: ProjectCreate, user_id: int
) -> Project:
    """
    Create a new project for user.

    Args:
        session: AsyncSession for database operations
        project: ProjectCreate object
        user_id: ID of the user creating the project

    Returns:
        Created project object
    """
    new_project = Project(**project.__dict__)
    # Set user_id from parameter (not included in ProjectCreate schema)
    new_project.user_id = user_id
    session.add(new_project)
    await session.commit()
    await session.refresh(new_project)

    return new_project


async def get_user_projects_service(
    session: AsyncSession, user_id: int
) -> List[Project]:
    """
    Get all projects for a user.

    Args:
        session: AsyncSession for database operations
        user_id: ID of the user

    Returns:
        List of project objects
    """
    # Query database for all projects owned by user
    statement = select(Project).where(Project.user_id == user_id)
    result = await session.execute(statement)
    user_projects = result.scalars().all()
    # Convert Sequence to List for consistency
    return list(user_projects)


async def assign_task_to_project_service(
    session: AsyncSession, project_id: int, task_id: int, user_id: int
) -> Task:
    """
    Assign a task to a project.

    Args:
        session: AsyncSession for database operations
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
    project_stmt = select(Project).where(Project.id == project_id)
    result = await session.execute(project_stmt)
    project = result.scalars().first()
    if not project:
        raise NotFoundException("Project", project_id)
    if project.user_id != user_id:
        raise ForbiddenException("You don't have permission to access this project")

    # Verify task exists and user has permission
    task_stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(task_stmt)
    task = result.scalars().first()
    if not task:
        raise NotFoundException("Task", task_id)
    if task.user_id != user_id:
        raise ForbiddenException("You don't have permission to access this task")

    # Assign task to project with updated timestamp
    task.project_id = project_id
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task
