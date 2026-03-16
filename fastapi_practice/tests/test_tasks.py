"""
Test Task CRUD & Authorization

Comprehensive tests covering:
- CRUD operations (Create, Read, Update, Delete)
- Access control (own tasks vs other users)
- Filtering, searching,pagination
- Error cases and validation
"""

import pytest
from fastapi import status
from datetime import datetime, timezone
from app.db.storage import tasks_db, task_id_counter


@pytest.fixture
def create_test_task(client, auth_headers, test_user):
    """
    Helper fixture to create test tasks for current user.

    Returns:
        Callable that creates a task with given parameters
    """

    def _create_task(title, status_val="todo", description=None):
        response = client.post(
            "/tasks",
            json={
                "title": title,
                "description": description,
                "status": status_val,
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        return response.json()

    return _create_task


class TestTaskCreate:
    """Test task creation."""

    def test_create_task_success(self, client, auth_headers):
        """Test successful task creation."""
        response = client.post(
            "/tasks",
            json={
                "title": "Learn FastAPI",
                "description": "Complete FastAPI tutorial",
                "status": "todo",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Learn FastAPI"
        assert data["description"] == "Complete FastAPI tutorial"
        assert data["status"] == "todo"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

    def test_create_task_without_auth(self, client):
        """Test task creation without authentication fails."""
        response = client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "status": "todo",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_task_missing_title(self, client, auth_headers):
        """Test task creation without title fails."""
        response = client.post(
            "/tasks",
            json={"status": "todo"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_task_with_default_status(self, client, auth_headers):
        """Test task creation with default status."""
        response = client.post(
            "/tasks",
            json={"title": "Task without status"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "todo"

    def test_create_task_invalid_status(self, client, auth_headers):
        """Test creating task with invalid status."""
        response = client.post(
            "/tasks",
            json={
                "title": "Test",
                "status": "invalid_status",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTaskRead:
    """Test task retrieval operations."""

    def test_get_all_tasks_empty(self, client, auth_headers):
        """Test getting tasks when none exist."""
        response = client.get("/tasks", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_get_all_tasks(self, client, auth_headers, create_test_task):
        """Test getting all tasks for current user."""
        create_test_task("Task 1", "todo")
        create_test_task("Task 2", "in_progress")

        response = client.get("/tasks", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        titles = [task["title"] for task in data["data"]]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert data["pagination"]["total"] == 2

    def test_get_task_by_id_success(self, client, auth_headers, create_test_task):
        """Test getting a specific task by ID."""
        task = create_test_task("Important Task", "in_progress")

        response = client.get(f"/tasks/{task['id']}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Important Task"
        assert data["status"] == "in_progress"

    def test_get_task_not_found(self, client, auth_headers):
        """Test getting non-existent task."""
        response = client.get("/tasks/999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_tasks_without_auth(self, client):
        """Test getting tasks without auth token."""
        response = client.get("/tasks")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_tasks_pagination(
        self, client, auth_headers, test_user, create_test_task
    ):
        """Test task pagination."""
        # Create 10 tasks
        for i in range(10):
            create_test_task(f"Task {i + 1}", "todo")

        # Get first page with limit=5
        response = client.get("/tasks?page=1&limit=5", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 5
        assert data["pagination"]["total"] == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["pages"] == 2
        assert data["pagination"]["has_more"] is True


class TestTaskUpdate:
    """Test task update operations."""

    def test_update_task_success(self, client, auth_headers, create_test_task):
        """Test successful task update."""
        task = create_test_task("Original Title", "todo")

        response = client.put(
            f"/tasks/{task['id']}",
            json={"title": "Updated Title", "status": "in_progress"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"

    def test_update_task_partial(self, client, auth_headers, create_test_task):
        """Test partial task update."""
        task = create_test_task("Original", "todo", "Original description")

        response = client.put(
            f"/tasks/{task['id']}",
            json={"status": "done"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Original"
        assert data["status"] == "done"

    def test_update_task_not_found(self, client, auth_headers):
        """Test updating non-existent task."""
        response = client.put(
            "/tasks/999",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_invalid_status(self, client, auth_headers, create_test_task):
        """Test updating with invalid status."""
        task = create_test_task("Task", "todo")

        response = client.put(
            f"/tasks/{task['id']}",
            json={"status": "unknown"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTaskDelete:
    """Test task deletion."""

    def test_delete_task_success(self, client, auth_headers, create_test_task):
        """Test successful task deletion."""
        task = create_test_task("Task to Delete")

        response = client.delete(f"/tasks/{task['id']}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

        # Verify task is deleted
        get_response = client.get(f"/tasks/{task['id']}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting non-existent task fails."""
        response = client.delete("/tasks/999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_without_auth(self, client, test_user):
        """Test deleting task without authentication fails."""
        response = client.delete("/tasks/999")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTaskFiltering:
    """Test task filtering and searching."""

    def test_filter_by_status(self, client, auth_headers, create_test_task):
        """Test filtering tasks by status."""
        create_test_task("Task 1", "todo")
        create_test_task("Task 2", "in_progress")
        create_test_task("Task 3", "todo")

        response = client.get(
            "/tasks?status=todo",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        assert all(task["status"] == "todo" for task in data["data"])

    def test_filter_by_invalid_status(self, client, auth_headers):
        """Test filtering with invalid status fails."""
        response = client.get(
            "/tasks?status=invalid_status",
            headers=auth_headers,
        )

        # Invalid status returns 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_by_title_case_insensitive(
        self, client, auth_headers, create_test_task
    ):
        """Test case-insensitive title search."""
        create_test_task("Learn FastAPI", "todo")
        create_test_task("Python Basics", "todo")

        # Search lowercase
        response_lower = client.get(
            "/tasks?search=fastapi",
            headers=auth_headers,
        )

        # Search uppercase
        response_upper = client.get(
            "/tasks?search=FASTAPI",
            headers=auth_headers,
        )

        assert response_lower.status_code == status.HTTP_200_OK
        assert response_upper.status_code == status.HTTP_200_OK
        assert len(response_lower.json()["data"]) == 1
        assert len(response_upper.json()["data"]) == 1

    def test_search_by_title_partial_match(
        self, client, auth_headers, create_test_task
    ):
        """Test partial title search."""
        create_test_task("Learn FastAPI", "todo")
        create_test_task("FastAPI Documentation", "todo")
        create_test_task("Python Basics", "todo")

        response = client.get(
            "/tasks?search=api",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    def test_sort_by_created_at(self, client, auth_headers, create_test_task):
        """Test sorting tasks by creation date."""
        create_test_task("Task 1", "todo")
        create_test_task("Task 2", "todo")
        create_test_task("Task 3", "todo")

        response = client.get(
            "/tasks?sort_by=created_at&sort_direction=asc",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        titles = [task["title"] for task in data["data"]]
        # Should be sorted by creation in ascending order
        assert titles[0] == "Task 1"
        assert titles[1] == "Task 2"


class TestTaskAuthorization:
    """Test task authorization and data isolation."""

    def test_tasks_isolated_by_user(
        self, client, auth_headers, auth_headers_user_2, create_test_task
    ):
        """Test that users can only see their own tasks."""
        # User 1 creates tasks
        create_test_task("User 1 Task 1", "todo")
        create_test_task("User 1 Task 2", "todo")

        # User 1 should see 2 tasks
        user1_response = client.get("/tasks", headers=auth_headers)
        assert len(user1_response.json()["data"]) == 2

        # User 2 should see 0 tasks (didn't create any)
        user2_response = client.get("/tasks", headers=auth_headers_user_2)
        assert len(user2_response.json()["data"]) == 0

    def test_get_task_other_user_forbidden(
        self, client, auth_headers, auth_headers_user_2, create_test_task
    ):
        """Test accessing other user's task returns 403 Forbidden."""
        # User 1 creates task
        task = create_test_task("User 1 Task")

        # User 2 tries to access it
        response = client.get(f"/tasks/{task['id']}", headers=auth_headers_user_2)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        # Response format: {"error": {"detail": "...", "message": "...", "status_code": 403}}
        assert "error" in data or "detail" in data

    def test_update_other_user_task_forbidden(
        self, client, auth_headers, auth_headers_user_2, create_test_task
    ):
        """Test other user cannot update task."""
        # User 1 creates task
        task = create_test_task("User 1 Task")

        # User 2 tries to update
        response = client.put(
            f"/tasks/{task['id']}",
            json={"title": "Hacked Title"},
            headers=auth_headers_user_2,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify task wasn't changed
        get_response = client.get(f"/tasks/{task['id']}", headers=auth_headers)
        assert get_response.json()["title"] == "User 1 Task"

    def test_delete_other_user_task_forbidden(
        self, client, auth_headers, auth_headers_user_2, create_test_task
    ):
        """Test other user cannot delete task."""
        # User 1 creates task
        task = create_test_task("User 1 Task")

        # User 2 tries to delete
        response = client.delete(f"/tasks/{task['id']}", headers=auth_headers_user_2)

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify task still exists
        get_response = client.get(f"/tasks/{task['id']}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK

    def test_cannot_view_deleted_other_user_task(
        self, client, auth_headers, auth_headers_user_2, create_test_task
    ):
        """Test cannot view task after user deletes their own."""
        # User 1 creates and deletes task
        task = create_test_task("User 1 Task")
        client.delete(f"/tasks/{task['id']}", headers=auth_headers)

        # User 2 tries (should also get 404, not 403)
        response = client.get(f"/tasks/{task['id']}", headers=auth_headers_user_2)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskErrorCases:
    """Test error handling for edge cases."""

    def test_create_task_empty_title(self, client, auth_headers):
        """Test creating task with empty title."""
        response = client.post(
            "/tasks",
            json={"title": ""},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_title_too_long(self, client, auth_headers):
        """Test creating task with title that exceeds max length."""
        response = client.post(
            "/tasks",
            json={"title": "x" * 201},  # Max is 200
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_description_too_long(self, client, auth_headers):
        """Test creating task with description that exceeds max length."""
        response = client.post(
            "/tasks",
            json={"title": "Task", "description": "x" * 2001},  # Max is 2000
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_task_invalid_id_format(self, client, auth_headers):
        """Test getting task with invalid ID format."""
        response = client.get("/tasks/invalid_id", headers=auth_headers)

        # FastAPI will return 422 for invalid integer
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_pagination_invalid_page(self, client, auth_headers):
        """Test pagination with invalid page number."""
        response = client.get("/tasks?page=0", headers=auth_headers)

        # Page must be >= 1
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_pagination_exceed_max_limit(self, client, auth_headers):
        """Test pagination with limit exceeding maximum."""
        response = client.get("/tasks?limit=101", headers=auth_headers)

        # Max limit is 100
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTaskDataConsistency:
    """Test data consistency and edge cases."""

    def test_created_task_has_timestamps(self, client, auth_headers):
        """Test that created task includes timestamps."""
        response = client.post(
            "/tasks",
            json={"title": "New Task"},
            headers=auth_headers,
        )

        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_updated_task_timestamp_changed(
        self, client, auth_headers, create_test_task
    ):
        """Test that updated_at changes on update."""
        task = create_test_task("Original")
        original_updated_at = task["updated_at"]

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.1)

        response = client.put(
            f"/tasks/{task['id']}",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        updated_task = response.json()
        assert updated_task["updated_at"] > original_updated_at

    def test_user_id_preserved_on_update(
        self, client, auth_headers, test_user, create_test_task
    ):
        """Test that user_id doesn't change on update."""
        task = create_test_task("Task")
        original_user_id = task["user_id"]

        response = client.put(
            f"/tasks/{task['id']}",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        updated_task = response.json()
        assert updated_task["user_id"] == original_user_id
        assert updated_task["user_id"] == test_user["id"]
