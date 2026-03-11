"""
Tests for user authentication endpoints.

Tests cover:
- User registration (POST /users/register)
- User login (POST /users/login)
- Access protected endpoints with valid token
"""


class TestRegister:
    """Test user registration endpoint."""

    def test_register_success(self, client, test_user_data):
        """
        Test successful user registration.

        Should return 201 Created with user data.
        """
        response = client.post(
            "/users/register",
            json=test_user_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["role"] == "user"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user_data, test_user):
        """
        Test registration with already registered email.

        Should return 400 Bad Request with error message.
        """
        response = client.post(
            "/users/register",
            json=test_user_data,
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["detail"] == "Email already registered"

    def test_register_invalid_email(self, client):
        """
        Test registration with invalid email format.

        Should return 422 Unprocessable Entity (Pydantic validation error).
        """
        response = client.post(
            "/users/register",
            json={
                "email": "invalid-email",
                "password": "validpass123",
            },
        )

        assert response.status_code == 422

    def test_register_short_password(self, client):
        """
        Test registration with password less than 8 characters.

        Should return 422 Unprocessable Entity (Pydantic validation error).
        """
        response = client.post(
            "/users/register",
            json={
                "email": "test@example.com",
                "password": "short",
            },
        )

        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        """
        Test registration with missing required fields.

        Should return 422 Unprocessable Entity.
        """
        response = client.post(
            "/users/register",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 422


class TestLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, test_user, test_user_data):
        """
        Test successful login.

        Should return 200 OK with JWT token.
        """
        response = client.post(
            "/users/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_email(self, client):
        """
        Test login with non-existent email.

        Should return 401 Unauthorized.
        """
        response = client.post(
            "/users/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["status_code"] == 401

    def test_login_wrong_password(self, client, test_user, test_user_data):
        """
        Test login with wrong password.

        Should return 401 Unauthorized.
        """
        response = client.post(
            "/users/login",
            data={
                "username": test_user_data["email"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_login_missing_fields(self, client):
        """
        Test login with missing fields.

        Should return 422 Unprocessable Entity.
        """
        response = client.post(
            "/users/login",
            data={"username": "test@example.com"},
        )

        assert response.status_code == 422


class TestProtectedEndpoint:
    """Test access to protected endpoints with authentication."""

    def test_get_profile_with_valid_token(self, client, test_user, auth_headers):
        """
        Test accessing protected endpoint with valid token.

        Should return 200 OK with user data.
        """
        response = client.get(
            "/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user["id"]
        assert data["email"] == test_user["email"]

    def test_get_profile_without_token(self, client):
        """
        Test accessing protected endpoint without token.

        Should return 401 Unauthorized (FastAPI OAuth2 returns 401 for missing token).
        """
        response = client.get("/users/me")

        assert response.status_code == 401

    def test_get_profile_with_invalid_token(self, client):
        """
        Test accessing protected endpoint with invalid token.

        Should return 401 Unauthorized.
        """
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["status_code"] == 401

    def test_get_profile_with_expired_token(self, client, test_user):
        """
        Test accessing protected endpoint with expired token.

        Should return 401 Unauthorized.
        """
        # Create an expired token (already handled by the decode_token function)
        from core.security import create_access_token
        from datetime import timedelta

        expired_token = create_access_token(
            data={"sub": test_user["email"]},
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_get_profile_with_malformed_header(self, client):
        """
        Test accessing protected endpoint with malformed auth header.

        Should return 401 Unauthorized.
        """
        response = client.get(
            "/users/me",
            headers={"Authorization": "InvalidFormat token"},
        )

        assert response.status_code == 401


class TestUpdateProfile:
    """Test profile update endpoint."""

    def test_update_email(self, client, test_user, auth_headers):
        """
        Test updating user email.

        Should return 200 OK with updated user data.
        """
        response = client.put(
            "/users/me",
            json={"email": "newemail@example.com"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"

    def test_update_password(self, client, test_user, auth_headers):
        """
        Test updating user password.

        Should return 200 OK and allow login with new password.
        """
        new_password = "newpass123"

        response = client.put(
            "/users/me",
            json={"password": new_password},
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Try login with new password
        login_response = client.post(
            "/users/login",
            data={
                "username": test_user["email"],
                "password": new_password,
            },
        )

        assert login_response.status_code == 200

    def test_update_duplicate_email(self, client, test_user, auth_headers):
        """
        Test updating to an email that already exists.

        Should return 400 Bad Request.
        """
        # Create another user
        from db.storage import users_db, user_id_counter
        from core.hashing import hash_password

        other_user_id = user_id_counter["id"]
        user_id_counter["id"] += 1
        users_db[other_user_id] = {
            "id": other_user_id,
            "email": "other@example.com",
            "hashed_password": hash_password("otherpass123"),
            "is_active": True,
            "role": "user",
        }

        # Try to update current user's email to the other user's email
        response = client.put(
            "/users/me",
            json={"email": "other@example.com"},
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_update_invalid_role_as_user(self, client, auth_headers):
        """
        Test updating role as non-admin user.

        Should return 403 Forbidden.
        """
        response = client.put(
            "/users/me",
            json={"role": "admin"},
            headers=auth_headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
