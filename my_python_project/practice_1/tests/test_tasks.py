"""
Tests for task CRUD operations.

Tests cover:
- Create task (POST /tasks)
- Read all tasks (GET /tasks)
- Read specific task (GET /tasks/{id})
- Update task (PUT /tasks/{id})
- Delete task (DELETE /tasks/{id})
"""


class TestCreateTask:
    """Test task creation endpoint."""

    def test_create_task_success(self, client, auth_headers):
        """
        Test successful task creation.

        Should return 201 Created with task data.
        """
        task_data = {
            "title": "Test Task",
            "description": "Test task description",
            "status": "todo",
        }

        response = client.post(
            "/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == "todo"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_minimal(self, client, auth_headers):
        """
        Test task creation with minimal fields.

        Description is optional, status defaults to 'todo'.
        """
        task_data = {"title": "Minimal Task"}

        response = client.post(
            "/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["status"] == "todo"
        assert data["description"] is None

    def test_create_task_invalid_status(self, client, auth_headers):
        """
        Test task creation with invalid status.

        Should return 422 Unprocessable Entity.
        """
        task_data = {
            "title": "Test Task",
            "status": "invalid_status",
        }

        response = client.post(
            "/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_task_missing_title(self, client, auth_headers):
        """
        Test task creation without title.

        Should return 422 Unprocessable Entity.
        """
        response = client.post(
            "/tasks",
            json={"description": "No title task"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_task_without_auth(self, client):
        """
        Test task creation without authentication.

        Should return 401 Unauthorized.
        """
        response = client.post(
            "/tasks",
            json={"title": "Unauth Task"},
        )

        assert response.status_code == 401


class TestGetTasks:
    """Test task retrieval endpoints."""

    def test_get_all_tasks_empty(self, client, auth_headers):
        """
        Test getting tasks when none exist.

        Should return 200 OK with empty list.
        """
        response = client.get(
            "/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_get_all_tasks(self, client, auth_headers, test_user):
        """
        Test getting all tasks for current user.

        Should return 200 OK with user's tasks only.
        """
        from db.storage import tasks_db, task_id_counter
        from datetime import datetime, timezone

        # Create test tasks
        for i in range(3):
            task_id = task_id_counter["id"]
            task_id_counter["id"] += 1
            tasks_db[task_id] = {
                "id": task_id,
                "user_id": test_user["id"],
                "title": f"Task {i + 1}",
                "description": None,
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

        response = client.get(
            "/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 3
        assert len(data["data"]) == 3

    def test_get_tasks_pagination(self, client, auth_headers, test_user):
        """
        Test task pagination.

        Should respect page and limit parameters.
        """
        from db.storage import tasks_db, task_id_counter
        from datetime import datetime, timezone

        # Create 10 test tasks
        for i in range(10):
            task_id = task_id_counter["id"]
            task_id_counter["id"] += 1
            tasks_db[task_id] = {
                "id": task_id,
                "user_id": test_user["id"],
                "title": f"Task {i + 1}",
                "description": None,
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

        # Get first page with limit=5
        response = client.get(
            "/tasks?page=1&limit=5",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 5
        assert data["pagination"]["total"] == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["pages"] == 2
        assert data["pagination"]["has_more"] is True

    def test_get_single_task(self, client, auth_headers, test_user):
        """
        Test getting a specific task by ID.

        Should return 200 OK with task data.
        """
        from db.storage import tasks_db, task_id_counter
        from datetime import datetime, timezone

        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "Single Task",
            "description": "Test description",
            "status": "in_progress",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        response = client.get(
            f"/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Single Task"

    def test_get_task_not_found(self, client, auth_headers):
        """
        Test getting non-existent task.

        Should return 404 Not Found.
        """
        response = client.get(
            "/tasks/999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestUpdateTask:
    """Test task update endpoint."""

    def test_update_task_title(self, client, auth_headers, test_user):
        """
        Test updating task title.

        Should return 200 OK with updated data.
        """
        from db.storage import tasks_db, task_id_counter
        from datetime import datetime, timezone

        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "Original Title",
            "description": None,
            "status": "todo",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        response = client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_task_status(self, client, auth_headers, test_user):
        """
        Test updating task status.

        Should return 200 OK with new status.
        """
        from db.storage import tasks_db, task_id_counter
        from datetime import datetime, timezone

        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "Test Task",
            "description": None,
            "status": "todo",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        response = client.put(
            f"/tasks/{task_id}",
            json={"status": "done"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"

    def test_update_task_multiple_fields(self, client, auth_headers, test_user):
        """
        Test updating multiple task fields at once.

        Should return 200 OK with all updates applied.
        """
        from db.storage import tasks_db, task_id_counter
        from datetime import datetime, timezone

        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "Original",
            "description": "Original desc",
            "status": "todo",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        response = client.put(
            f"/tasks/{task_id}",
            json={
                "title": "New Title",
                "description": "New Description",
                "status": "in_progress",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "New Description"
        assert data["status"] == "in_progress"

    def test_update_task_not_found(self, client, auth_headers):
        """
        Test updating non-existent task.

        Should return 404 Not Found.
        """
        response = client.put(
            "/tasks/999",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestDeleteTask:
    """Test task deletion endpoint."""

    def test_delete_task_success(self, client, auth_headers, test_user):
        """
        Test successful task deletion.

        Should return 200 OK with success message.
        """
        from db.storage import tasks_db, task_id_counter
        from datetime import datetime, timezone

        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "Task to Delete",
            "description": None,
            "status": "todo",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        response = client.delete(
            f"/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

        # Verify task is deleted
        assert task_id not in tasks_db

    def test_delete_task_not_found(self, client, auth_headers):
        """
        Test deleting non-existent task.

        Should return 404 Not Found.
        """
        response = client.delete(
            "/tasks/999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_delete_task_without_auth(self, client, test_user):
        """
        Test deleting task without authentication.

        Should return 401 Unauthorized (no token provided).
        """
        from db.storage import tasks_db, task_id_counter
        from datetime import datetime, timezone

        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "Task",
            "description": None,
            "status": "todo",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        response = client.delete(f"/tasks/{task_id}")

        assert response.status_code == 401
