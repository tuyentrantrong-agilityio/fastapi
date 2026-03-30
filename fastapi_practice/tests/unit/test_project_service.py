"""Unit tests for project service functions with mocked AsyncSession."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.services.project_service import (
    create_project_service,
    get_user_projects_service,
    assign_task_to_project_service,
)
from app.schemas.project import ProjectCreate
from app.models.project import Project
from app.models.task import Task
from app.core.exceptions import NotFoundException, ForbiddenException


def make_project(id=1, user_id=1, name="Project", description=None):
    """Helper to create Project model instance."""
    project = Project(
        id=id,
        user_id=user_id,
        name=name,
        description=description,
    )
    return project


def make_task(id=1, user_id=1, title="Task", status="todo", project_id=None):
    """Helper to create Task model instance."""
    task = Task(
        id=id,
        user_id=user_id,
        title=title,
        status=status,
        project_id=project_id,
    )
    return task


class TestCreateProjectService:
    """Test cases for create_project_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Should successfully create project."""

        # --- Mock session and DB operations ---
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Prepare input DTO ---
        project_create = ProjectCreate(
            name="New Project", description="Project Description"
        )

        # --- Mock DB refresh to assign ID ---
        def side_effect_refresh(proj):
            proj.id = 1

        session.refresh.side_effect = side_effect_refresh

        # --- Call the service function under test ---
        result = await create_project_service(session, project_create, user_id=1)

        # --- Assert project was created with correct values ---
        session.add.assert_called_once()  # Project added to session
        session.commit.assert_awaited_once()  # Changes committed
        session.refresh.assert_awaited_once()  # Project refreshed with DB-assigned ID
        assert result.name == "New Project"  # Name set
        assert result.user_id == 1  # Owner set

    @pytest.mark.asyncio
    async def test_name_only(self):
        """Should create project with name only."""

        # --- Mock session and DB operations ---
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Prepare minimal input DTO (name only) ---
        project_create = ProjectCreate(name="Simple Project")

        # --- Call the service function under test ---
        result = await create_project_service(session, project_create, user_id=1)

        # --- Assert project created with minimal input ---
        assert result.name == "Simple Project"
        assert result.user_id == 1  # Owner set
        session.add.assert_called_once()  # Project added to session


class TestGetUserProjectsService:
    """Test cases for get_user_projects_service."""

    @pytest.mark.asyncio
    async def test_empty(self):
        """Should return empty list when no projects exist."""

        # --- Mock session with no projects ---
        session = AsyncMock(spec=AsyncSession)
        query_result = MagicMock()
        query_result.scalars.return_value.all.return_value = []  # Simulate: no projects found
        session.execute.return_value = query_result

        # --- Call the service function under test ---
        result = await get_user_projects_service(session, user_id=1)

        # --- Assert empty result returned ---
        assert result == []  # No projects
        session.execute.assert_awaited_once()  # Query executed

    @pytest.mark.asyncio
    async def test_multiple(self):
        """Should return all projects for user."""

        # --- Mock session and project instances ---
        session = AsyncMock(spec=AsyncSession)
        project1 = make_project(id=1, user_id=1, name="Project 1")
        project2 = make_project(id=2, user_id=1, name="Project 2")

        # --- Mock query to return both projects ---
        query_result = MagicMock()
        query_result.scalars.return_value.all.return_value = [
            project1,
            project2,
        ]  # Simulate: 2 projects found
        session.execute.return_value = query_result

        # --- Call the service function under test ---
        result = await get_user_projects_service(session, user_id=1)

        # --- Assert all projects returned ---
        assert len(result) == 2  # 2 projects returned
        assert result[0].name == "Project 1"  # First project
        assert result[1].name == "Project 2"  # Second project

    @pytest.mark.asyncio
    async def test_filters_by_user(self):
        """Should only return projects for specific user."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Create projects for different users ---
        project1 = make_project(id=1, user_id=1, name="User 1 Project")
        project2 = make_project(id=2, user_id=2, name="User 2 Project")

        # --- Mock query to return only user 2's project ---
        query_result = MagicMock()
        query_result.scalars.return_value.all.return_value = [
            project2
        ]  # Only project2 for user 2
        session.execute.return_value = query_result

        # --- Call the service for user 2 ---
        result = await get_user_projects_service(session, user_id=2)

        # --- Assert only user 2's project returned ---
        assert len(result) == 1  # Only 1 project
        assert result[0].user_id == 2  # Correct user
        assert result[0].name == "User 2 Project"  # Correct project


class TestAssignTaskToProjectService:
    """Test cases for assign_task_to_project_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Should successfully assign task to project."""

        # --- Mock session, project, and task ---
        session = AsyncMock(spec=AsyncSession)
        project = make_project(id=1, user_id=1)
        task = make_task(id=1, user_id=1, project_id=None)  # Task not yet assigned

        # --- Mock project lookup ---
        project_query = MagicMock()
        project_query.scalars.return_value.first.return_value = project

        # --- Mock task lookup ---
        task_query = MagicMock()
        task_query.scalars.return_value.first.return_value = task

        # --- Mock session to return project query first, then task query ---
        session.execute.side_effect = [project_query, task_query]
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Call the service function under test ---
        result = await assign_task_to_project_service(
            session, project_id=1, task_id=1, user_id=1
        )

        # --- Assert task assigned to project ---
        assert result.project_id == 1  # Task now belongs to project
        assert result.id == 1  # Correct task

    @pytest.mark.asyncio
    async def test_project_not_found(self):
        """Should raise error if project not found."""

        # --- Mock session with no project found ---
        session = AsyncMock(spec=AsyncSession)
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = (
            None  # Simulate: project doesn't exist
        )
        session.execute.return_value = query_result

        # --- Call and verify exception is raised ---
        with pytest.raises(NotFoundException):
            await assign_task_to_project_service(
                session, project_id=999, task_id=1, user_id=1
            )

    @pytest.mark.asyncio
    async def test_task_not_found(self):
        """Should raise error if task not found."""

        # --- Mock session, project exists but task doesn't ---
        session = AsyncMock(spec=AsyncSession)
        project = make_project(id=1, user_id=1)

        # --- Mock project lookup (found) ---
        project_query = MagicMock()
        project_query.scalars.return_value.first.return_value = project

        # --- Mock task lookup (not found) ---
        task_query = MagicMock()
        task_query.scalars.return_value.first.return_value = (
            None  # Simulate: task doesn't exist
        )

        # --- Mock session to return project query first, then task query ---
        session.execute.side_effect = [project_query, task_query]

        # --- Call and verify exception is raised ---
        with pytest.raises(NotFoundException):
            await assign_task_to_project_service(
                session, project_id=1, task_id=999, user_id=1
            )

    @pytest.mark.asyncio
    async def test_user_not_own_project(self):
        """Should raise error if user doesn't own project."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Create project owned by user 1 ---
        project = make_project(id=1, user_id=1)  # Owned by user 1

        # --- Mock project lookup ---
        project_query = MagicMock()
        project_query.scalars.return_value.first.return_value = project
        session.execute.return_value = project_query

        # --- Call with different user (user 2) and verify permission error ---
        with pytest.raises(ForbiddenException):
            await assign_task_to_project_service(
                session,
                project_id=1,
                task_id=1,
                user_id=2,  # Different user
            )

    @pytest.mark.asyncio
    async def test_user_not_own_task(self):
        """Should raise error if user doesn't own task."""

        # --- Mock session, project, and task ---
        session = AsyncMock(spec=AsyncSession)
        project = make_project(id=1, user_id=1)  # Owned by user 1
        task = make_task(id=1, user_id=2, project_id=None)  # Owned by user 2

        # --- Mock project lookup (found) ---
        project_query = MagicMock()
        project_query.scalars.return_value.first.return_value = project

        # --- Mock task lookup (found but different owner) ---
        task_query = MagicMock()
        task_query.scalars.return_value.first.return_value = task

        # --- Mock session to return project query first, then task query ---
        session.execute.side_effect = [project_query, task_query]

        # --- Call and verify permission error (mismatched ownership) ---
        with pytest.raises(ForbiddenException):
            await assign_task_to_project_service(
                session,
                project_id=1,
                task_id=1,
                user_id=1,  # User 1 owns project but not task
            )
