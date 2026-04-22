"""
Tests for project endpoints.

Tests cover:
- Project creation (POST /projects)
- Get all projects (GET /projects)
- Assign tasks to projects (POST /projects/{id}/tasks/{id})
"""

import pytest


@pytest.fixture
def create_test_project(client, auth_headers):
    """Create a test project for the authorized user"""
    payload = {
        "name": "Test Project",
        "description": "A test project",
    }
    response = client.post("/projects", json=payload, headers=auth_headers)
    if response.status_code != 201:
        raise ValueError(
            f"Failed to create test project. Status: {response.status_code}, "
            f"Response: {response.text}"
        )
    return response.json()


@pytest.fixture
def create_test_task(client, auth_headers):
    """Create a test task for the authorized user"""
    payload = {
        "title": "Test Task",
        "description": "A test task",
    }
    response = client.post("/tasks", json=payload, headers=auth_headers)
    if response.status_code != 201:
        raise ValueError(
            f"Failed to create test task. Status: {response.status_code}, "
            f"Response: {response.text}"
        )
    return response.json()


class TestCreateProject:
    """Test project creation"""

    def test_create_project_success(self, client, auth_headers):
        """Test successful project creation"""
        payload = {
            "name": "New Project",
            "description": "A new project",
        }
        response = client.post("/projects", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Project"
        assert data["description"] == "A new project"

    def test_create_project_missing_name(self, client, auth_headers):
        """Test project creation without name"""
        payload = {
            "description": "A project without name",
        }
        response = client.post("/projects", json=payload, headers=auth_headers)

        assert response.status_code == 422

    def test_create_project_duplicate_name(self, client, auth_headers):
        """Test creating projects with duplicate names"""
        payload = {
            "name": "Duplicate Project",
            "description": "First creation",
        }

        # Create first project
        response1 = client.post("/projects", json=payload, headers=auth_headers)
        assert response1.status_code == 201

        # Create another with same name (app may allow)
        response2 = client.post("/projects", json=payload, headers=auth_headers)
        assert response2.status_code == 201

    def test_create_project_unauthorized(self, client):
        """Test project creation without token"""
        payload = {
            "name": "Unauthorized Project",
            "description": "No token",
        }
        response = client.post("/projects", json=payload)
        assert response.status_code == 401


class TestGetProjects:
    """Test getting projects"""

    def test_get_projects_empty(self, client, auth_headers):
        """Test getting projects when none exist"""
        response = client.get("/projects", headers=auth_headers)

        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) == 0

    def test_get_projects_single(self, client, auth_headers, create_test_project):
        """Test getting projects with one project"""
        response = client.get("/projects", headers=auth_headers)

        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) == 1
        assert projects[0]["name"] == "Test Project"

    def test_get_projects_multiple(self, client, auth_headers):
        """Test getting multiple projects"""
        # Create multiple projects
        for i in range(3):
            payload = {"name": f"Project {i}", "description": f"Description {i}"}
            client.post("/projects", json=payload, headers=auth_headers)

        response = client.get("/projects", headers=auth_headers)
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 3

    def test_get_projects_user_isolation(self, client, auth_headers, auth_headers_user_2):
        """Test that users only see their own projects"""
        # User 1 creates projects
        client.post(
            "/projects",
            json={"name": "User1 Project", "description": "For user 1"},
            headers=auth_headers,
        )

        # User 2 creates projects
        client.post(
            "/projects",
            json={"name": "User2 Project", "description": "For user 2"},
            headers=auth_headers_user_2,
        )

        # Check user 1 only sees their projects
        response = client.get("/projects", headers=auth_headers)
        projects = response.json()
        assert len(projects) == 1
        assert projects[0]["name"] == "User1 Project"

    def test_get_projects_unauthorized(self, client):
        """Test getting projects without token"""
        response = client.get("/projects")
        assert response.status_code == 401

    def test_get_projects_invalid_token(self, client):
        """Test getting projects with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/projects", headers=headers)
        assert response.status_code == 401

    def test_get_projects_empty_token(self, client):
        """Test getting projects with empty token"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/projects", headers=headers)
        assert response.status_code == 401


class TestAssignTaskToProject:
    """Test assigning tasks to projects"""

    def test_assign_task_to_project_success(
        self, client, auth_headers, create_test_project, create_test_task
    ):
        """Test successfully assigning task to project"""
        project_id = create_test_project["id"]
        task_id = create_test_task["id"]

        response = client.post(
            f"/projects/{project_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_assign_nonexistent_task(self, client, auth_headers, create_test_project):
        """Test assigning non-existent task to project"""
        project_id = create_test_project["id"]
        fake_task_id = "nonexistent_task"

        response = client.post(
            f"/projects/{project_id}/tasks/{fake_task_id}",
            headers=auth_headers,
        )

        assert response.status_code in [404, 422]

    def test_assign_to_nonexistent_project(self, client, auth_headers, create_test_task):
        """Test assigning task to non-existent project"""
        fake_project_id = "nonexistent_project"
        task_id = create_test_task["id"]

        response = client.post(
            f"/projects/{fake_project_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code in [404, 422]

    def test_assign_task_unauthorized(self, client, create_test_project, create_test_task):
        """Test assigning task without authorization"""
        project_id = create_test_project["id"]
        task_id = create_test_task["id"]

        response = client.post(f"/projects/{project_id}/tasks/{task_id}")

        assert response.status_code == 401

    def test_assign_other_user_task(
        self,
        client,
        auth_headers,
        auth_headers_user_2,
        create_test_project,
        create_test_task,
    ):
        """Test user 2 trying to assign user 1's task"""
        project_id = create_test_project["id"]
        task_id = create_test_task["id"]

        response = client.post(
            f"/projects/{project_id}/tasks/{task_id}",
            headers=auth_headers_user_2,
        )

        # Should be forbidden - user 2 doesn't own the project
        assert response.status_code in [403, 404]

    def test_assign_task_to_other_user_project(self, client, auth_headers, auth_headers_user_2):
        """Test user 2 assigning task to user 1's project"""
        # User 1 creates project and task
        project_response = client.post(
            "/projects",
            json={"name": "User1 Project", "description": "Test"},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        task_response = client.post(
            "/tasks",
            json={"title": "User1 Task", "description": "Test"},
            headers=auth_headers,
        )
        task_id = task_response.json()["id"]

        # User 2 tries to assign user 1's task to user 1's project
        response = client.post(
            f"/projects/{project_id}/tasks/{task_id}",
            headers=auth_headers_user_2,
        )

        # Should fail - user 2 doesn't own the project
        assert response.status_code in [403, 404]

    def test_assign_multiple_tasks(self, client, auth_headers, create_test_project):
        """Test assigning multiple tasks to one project"""
        project_id = create_test_project["id"]

        # Create and assign multiple tasks
        task_ids = []
        for i in range(3):
            task_response = client.post(
                "/tasks",
                json={"title": f"Task {i}", "description": f"Description {i}"},
                headers=auth_headers,
            )
            task_ids.append(task_response.json()["id"])

        # Assign all tasks
        for task_id in task_ids:
            response = client.post(
                f"/projects/{project_id}/tasks/{task_id}",
                headers=auth_headers,
            )
            assert response.status_code == 200

    def test_assign_task_twice(self, client, auth_headers, create_test_project, create_test_task):
        """Test assigning same task twice"""
        project_id = create_test_project["id"]
        task_id = create_test_task["id"]

        # First assignment
        response1 = client.post(
            f"/projects/{project_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response1.status_code == 200

        # Second assignment
        response2 = client.post(
            f"/projects/{project_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        # Could be 200 (idempotent) or 409 (conflict)
        assert response2.status_code in [200, 409]
