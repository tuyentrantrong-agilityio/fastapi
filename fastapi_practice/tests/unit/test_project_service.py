"""Unit tests for project service functions."""

import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from app.services.project_service import (
    create_project_service,
    get_user_projects_service,
    assign_task_to_project_service,
)
from app.schemas.project import ProjectCreate
from app.core.exceptions import NotFoundException, ForbiddenException


class TestCreateProjectService:
    """Test create_project_service function."""

    @pytest.mark.asyncio
    async def test_create_project_success(self):
        """Should successfully create project."""
        with (
            patch("app.services.project_service.projects_db", {}),
            patch("app.services.project_service.project_id_counter", {"id": 1}),
            patch("app.services.project_service.datetime") as mock_datetime,
        ):
            mock_datetime.now.return_value = datetime(2024, 1, 1, tzinfo=timezone.utc)

            project_create = ProjectCreate(
                name="New Project",
                description="Project Description",
            )

            result = await create_project_service(project_create, 1)

            assert result["name"] == "New Project"
            assert result["user_id"] == 1
            assert "id" in result

    @pytest.mark.asyncio
    async def test_create_project_name_only(self):
        """Should create project with name only."""
        with (
            patch("app.services.project_service.projects_db", {}),
            patch("app.services.project_service.project_id_counter", {"id": 1}),
            patch("app.services.project_service.datetime"),
        ):
            project_create = ProjectCreate(name="Simple Project")
            result = await create_project_service(project_create, 1)

            assert result["name"] == "Simple Project"

    @pytest.mark.asyncio
    async def test_create_project_increments_id(self):
        """Should increment project ID."""
        mock_counter = {"id": 5}

        with (
            patch("app.services.project_service.projects_db", {}),
            patch("app.services.project_service.project_id_counter", mock_counter),
            patch("app.services.project_service.datetime"),
        ):
            project_create = ProjectCreate(name="Project")
            await create_project_service(project_create, 1)

            assert mock_counter["id"] == 6


class TestGetUserProjectsService:
    """Test get_user_projects_service function."""

    @pytest.mark.asyncio
    async def test_get_projects_empty(self):
        """Should return empty list when no projects exist."""
        with patch("app.services.project_service.projects_db", {}):
            result = await get_user_projects_service(1)

            assert result == []

    @pytest.mark.asyncio
    async def test_get_all_user_projects(self):
        """Should return all projects for user."""
        mock_projects_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "name": "Project 1",
                "description": "Description 1",
                "created_at": datetime.now(timezone.utc),
            },
            2: {
                "id": 2,
                "user_id": 1,
                "name": "Project 2",
                "description": "Description 2",
                "created_at": datetime.now(timezone.utc),
            },
            3: {
                "id": 3,
                "user_id": 2,  # Different user
                "name": "Project 3",
                "description": "Description 3",
                "created_at": datetime.now(timezone.utc),
            },
        }

        with patch("app.services.project_service.projects_db", mock_projects_db):
            result = await get_user_projects_service(1)

            assert len(result) == 2
            assert all(project["user_id"] == 1 for project in result)
            assert result[0]["name"] == "Project 1"
            assert result[1]["name"] == "Project 2"

    @pytest.mark.asyncio
    async def test_get_projects_single_user(self):
        """Should only return projects for specific user."""
        mock_projects_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "name": "User 1 Project",
                "description": "Desc",
                "created_at": datetime.now(timezone.utc),
            },
            2: {
                "id": 2,
                "user_id": 2,
                "name": "User 2 Project",
                "description": "Desc",
                "created_at": datetime.now(timezone.utc),
            },
        }

        with patch("app.services.project_service.projects_db", mock_projects_db):
            result = await get_user_projects_service(2)

            assert len(result) == 1
            assert result[0]["user_id"] == 2
            assert result[0]["name"] == "User 2 Project"


class TestAssignTaskToProjectService:
    """Test assign_task_to_project_service function."""

    @pytest.mark.asyncio
    async def test_assign_task_success(self):
        """Should successfully assign task to project."""
        mock_projects_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "name": "Project",
                "description": "Desc",
                "created_at": datetime.now(timezone.utc),
            }
        }

        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "title": "Task",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        }

        with (
            patch("app.services.project_service.projects_db", mock_projects_db),
            patch("app.services.project_service.tasks_db", mock_tasks_db),
        ):
            result = await assign_task_to_project_service(1, 1, 1)

            assert result["project_id"] == 1
            assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_assign_task_project_not_found(self):
        """Should raise error if project not found."""
        with (
            patch("app.services.project_service.projects_db", {}),
            patch("app.services.project_service.tasks_db", {1: {}}),
        ):
            with pytest.raises(NotFoundException):
                await assign_task_to_project_service(1, 999, 1)

    @pytest.mark.asyncio
    async def test_assign_task_task_not_found(self):
        """Should raise error if task not found."""
        mock_projects_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "name": "Project",
                "description": "Desc",
                "created_at": datetime.now(timezone.utc),
            }
        }

        with (
            patch("app.services.project_service.projects_db", mock_projects_db),
            patch("app.services.project_service.tasks_db", {}),
        ):
            with pytest.raises(NotFoundException):
                await assign_task_to_project_service(1, 999, 1)

    @pytest.mark.asyncio
    async def test_assign_task_user_not_own_project(self):
        """Should raise error if user doesn't own project."""
        mock_projects_db = {
            1: {
                "id": 1,
                "user_id": 1,  # Different owner
                "name": "Project",
                "description": "Desc",
                "created_at": datetime.now(timezone.utc),
            }
        }

        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 2,
                "title": "Task",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        }

        with (
            patch("app.services.project_service.projects_db", mock_projects_db),
            patch("app.services.project_service.tasks_db", mock_tasks_db),
        ):
            # User 2 trying to assign to user 1's project
            with pytest.raises(ForbiddenException):
                await assign_task_to_project_service(1, 1, 2)

    @pytest.mark.asyncio
    async def test_assign_task_user_not_own_task(self):
        """Should raise error if user doesn't own task."""
        mock_projects_db = {
            1: {
                "id": 1,
                "user_id": 1,
                "name": "Project",
                "description": "Desc",
                "created_at": datetime.now(timezone.utc),
            }
        }

        mock_tasks_db = {
            1: {
                "id": 1,
                "user_id": 2,  # Different owner
                "title": "Task",
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        }

        with (
            patch("app.services.project_service.projects_db", mock_projects_db),
            patch("app.services.project_service.tasks_db", mock_tasks_db),
        ):
            # User 1 trying to assign user 2's task
            with pytest.raises(ForbiddenException):
                await assign_task_to_project_service(1, 1, 1)
