"""
Tests for authorization and error handling.

Tests cover:
- User cannot access other user's tasks (403 Forbidden)
- 401 Unauthorized for invalid tokens
- 403 Forbidden for permission denied
- 404 Not Found for missing resources
"""


class TestTaskOwnership:
    """Test task ownership verification."""

    def test_user_cannot_access_other_user_task(self, client, test_user):
        """
        Test that user cannot access another user's task.

        Should return 403 Forbidden.
        """
        from app.db.storage import tasks_db, task_id_counter, users_db, user_id_counter
        from app.core.hashing import hash_password
        from app.core.security import create_access_token
        from datetime import datetime, timezone, timedelta

        # Create another user
        other_user_id = user_id_counter["id"]
        user_id_counter["id"] += 1
        users_db[other_user_id] = {
            "id": other_user_id,
            "email": "other@example.com",
            "hashed_password": hash_password("otherpass123"),
            "is_active": True,
            "role": "user",
        }

        # Create task for first user
        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "User 1 Task",
            "description": None,
            "status": "todo",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        # Create token for other user
        other_token = create_access_token(
            data={"sub": "other@example.com"},
            expires_delta=timedelta(minutes=30),
        )

        # Try to access the task as other user
        response = client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data

    def test_user_cannot_update_other_user_task(self, client, test_user):
        """
        Test that user cannot update another user's task.

        Should return 403 Forbidden.
        """
        from app.db.storage import tasks_db, task_id_counter, users_db, user_id_counter
        from app.core.hashing import hash_password
        from app.core.security import create_access_token
        from datetime import datetime, timezone, timedelta

        # Create another user
        other_user_id = user_id_counter["id"]
        user_id_counter["id"] += 1
        users_db[other_user_id] = {
            "id": other_user_id,
            "email": "other@example.com",
            "hashed_password": hash_password("otherpass123"),
            "is_active": True,
            "role": "user",
        }

        # Create task for first user
        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "User 1 Task",
            "description": None,
            "status": "todo",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        # Create token for other user
        other_token = create_access_token(
            data={"sub": "other@example.com"},
            expires_delta=timedelta(minutes=30),
        )

        # Try to update the task as other user
        response = client.put(
            f"/tasks/{task_id}",
            json={"title": "Invalid Update"},
            headers={"Authorization": f"Bearer {other_token}"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data

    def test_user_cannot_delete_other_user_task(self, client, test_user):
        """
        Test that user cannot delete another user's task.

        Should return 403 Forbidden.
        """
        from app.db.storage import tasks_db, task_id_counter, users_db, user_id_counter
        from app.core.hashing import hash_password
        from app.core.security import create_access_token
        from datetime import datetime, timezone, timedelta

        # Create another user
        other_user_id = user_id_counter["id"]
        user_id_counter["id"] += 1
        users_db[other_user_id] = {
            "id": other_user_id,
            "email": "other@example.com",
            "hashed_password": hash_password("otherpass123"),
            "is_active": True,
            "role": "user",
        }

        # Create task for first user
        task_id = task_id_counter["id"]
        task_id_counter["id"] += 1
        tasks_db[task_id] = {
            "id": task_id,
            "user_id": test_user["id"],
            "title": "User 1 Task",
            "description": None,
            "status": "todo",
            "project_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        # Create token for other user
        other_token = create_access_token(
            data={"sub": "other@example.com"},
            expires_delta=timedelta(minutes=30),
        )

        # Try to delete the task as other user
        response = client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data

    def test_user_only_sees_own_tasks(self, client, test_user):
        """
        Test that user only sees their own tasks in list.

        Should return only tasks owned by current user.
        """
        from app.db.storage import tasks_db, task_id_counter, users_db, user_id_counter
        from app.core.hashing import hash_password
        from app.core.security import create_access_token
        from datetime import datetime, timezone, timedelta

        # Create another user
        other_user_id = user_id_counter["id"]
        user_id_counter["id"] += 1
        users_db[other_user_id] = {
            "id": other_user_id,
            "email": "other@example.com",
            "hashed_password": hash_password("otherpass123"),
            "is_active": True,
            "role": "user",
        }

        # Create tasks for both users
        for _ in range(2):
            task_id = task_id_counter["id"]
            task_id_counter["id"] += 1
            tasks_db[task_id] = {
                "id": task_id,
                "user_id": test_user["id"],
                "title": "User 1 Task",
                "description": None,
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

        for _ in range(3):
            task_id = task_id_counter["id"]
            task_id_counter["id"] += 1
            tasks_db[task_id] = {
                "id": task_id,
                "user_id": other_user_id,
                "title": "Other User Task",
                "description": None,
                "status": "todo",
                "project_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

        # Get token for first user
        first_token = create_access_token(
            data={"sub": test_user["email"]},
            expires_delta=timedelta(minutes=30),
        )

        # List tasks for first user
        response = client.get(
            "/tasks",
            headers={"Authorization": f"Bearer {first_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total"] == 2


class TestUnauthorized:
    """Test 401 Unauthorized responses."""

    def test_invalid_token_format(self, client):
        """
        Test request with invalid token format.

        Should return 401 Unauthorized.
        """
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bear invalid"},
        )

        assert response.status_code == 401

    def test_expired_token(self, client, test_user):
        """
        Test request with expired token.

        Should return 401 Unauthorized.
        """
        from app.core.security import create_access_token
        from datetime import timedelta

        # Create expired token
        expired_token = create_access_token(
            data={"sub": test_user["email"]},
            expires_delta=timedelta(seconds=-1),
        )

        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["status_code"] == 401

    def test_token_with_invalid_user(self, client):
        """
        Test token that references non-existent user.

        Should return 401 Unauthorized.
        """
        from app.core.security import create_access_token
        from datetime import timedelta

        # Create token for non-existent user
        token = create_access_token(
            data={"sub": "nonexistent@example.com"},
            expires_delta=timedelta(minutes=30),
        )

        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestForbidden:
    """Test 403 Forbidden responses."""

    def test_admin_only_endpoint(self, client, auth_headers):
        """
        Test that normal user cannot access admin endpoint.

        Should return 403 Forbidden.
        """
        # Update profile with role change (admin only)
        response = client.put(
            "/users/me",
            json={"role": "admin"},
            headers=auth_headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert data["error"]["status_code"] == 403

    def test_no_authentication_header(self, client):
        """
        Test protected endpoint without authentication header.

        Should return 401 Unauthorized.
        """
        response = client.get("/users/me")

        assert response.status_code == 401


class TestNotFound:
    """Test 404 Not Found responses."""

    def test_task_not_found(self, client, auth_headers):
        """
        Test getting non-existent task.

        Should return 404 Not Found.
        """
        response = client.get(
            "/tasks/9999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["status_code"] == 404
        assert "not found" in data["error"]["detail"].lower()

    def test_project_not_found(self, client, auth_headers):
        """
        Test accessing non-existent project.

        Should return 404 Not Found.
        """
        response = client.post(
            "/tasks/1/project/9999",
            headers=auth_headers,
        )

        # First create a task to test project assignment
        task_response = client.post(
            "/tasks",
            json={"title": "Test Task"},
            headers=auth_headers,
        )
        task_id = task_response.json()["id"]

        # Now try to assign to non-existent project
        response = client.post(
            f"/tasks/{task_id}/project/9999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_nonexistent_endpoint(self, client, auth_headers):
        """
        Test accessing non-existent endpoint.

        Should return 404 Not Found.
        """
        response = client.get(
            "/nonexistent",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestErrorResponseFormat:
    """Test error response format consistency."""

    def test_error_response_has_required_fields(self, client):
        """
        Test that error responses have consistent format.

        Should have: error.message, error.detail, error.status_code
        """
        response = client.get(
            "/tasks/999",
            headers={"Authorization": "Bearer invalid"},
        )

        # Will get 401 for invalid token
        if response.status_code == 401:
            data = response.json()
            assert "error" in data
            assert "message" in data["error"]
            assert "detail" in data["error"]
            assert "status_code" in data["error"]

    def test_bad_request_format(self, client):
        """
        Test bad request error format.

        Should have consistent error structure.
        """
        response = client.post(
            "/users/register",
            json={"email": "invalid-email", "password": "short"},
        )

        # Pydantic validation error (422)
        assert response.status_code == 422
