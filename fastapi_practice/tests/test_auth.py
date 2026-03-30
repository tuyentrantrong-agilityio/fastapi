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
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

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
        from app.core.security import create_access_token
        from datetime import timedelta

        expired_token = create_access_token(
            data={"sub": test_user.email},
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
                "username": test_user.email,
                "password": new_password,
            },
        )

        assert login_response.status_code == 200

    def test_update_duplicate_email(self, client, test_user, auth_headers):
        """
        Test updating to an email that already exists.

        Should return 400 Bad Request.
        """
        # Register another user to create duplicate email scenario
        other_email = "other@example.com"
        other_password = "otherpass123"

        register_response = client.post(
            "/users/register",
            json={
                "email": other_email,
                "password": other_password,
            },
        )
        assert register_response.status_code == 201

        # Try to update current user's email to the other user's email
        response = client.put(
            "/users/me",
            json={"email": other_email},
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


class TestAuthenticationFlow:
    """Test complete authentication workflow."""

    def test_full_auth_flow(self, client):
        """Test complete flow: register -> login -> access protected route."""
        # Step 1: Register
        new_user_email = "flowtest@example.com"
        new_user_password = "flowtestpass123"

        register_response = client.post(
            "/users/register",
            json={
                "email": new_user_email,
                "password": new_user_password,
            },
        )
        assert register_response.status_code == 201
        registered_user = register_response.json()
        assert registered_user["email"] == new_user_email

        # Step 2: Login
        login_response = client.post(
            "/users/login",
            data={
                "username": new_user_email,
                "password": new_user_password,
            },
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]
        assert len(access_token) > 0

        # Step 3: Access protected route with token
        protected_response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert protected_response.status_code == 200
        user_profile = protected_response.json()
        assert user_profile["email"] == new_user_email
        assert user_profile["id"] == registered_user["id"]

    def test_auth_flow_with_password_change(self, client):
        """Test full flow including password change and re-login."""
        # Register
        original_email = "passchange@example.com"
        original_password = "originalpass123"

        register_response = client.post(
            "/users/register",
            json={"email": original_email, "password": original_password},
        )
        assert register_response.status_code == 201

        # Login with original password
        login_response = client.post(
            "/users/login",
            data={"username": original_email, "password": original_password},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Change password
        new_password = "newpass123"
        update_response = client.put(
            "/users/me",
            json={"password": new_password},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200

        # Try login with original password (should fail)
        failed_login = client.post(
            "/users/login",
            data={"username": original_email, "password": original_password},
        )
        assert failed_login.status_code == 401

        # Login with new password (should succeed)
        new_login = client.post(
            "/users/login",
            data={"username": original_email, "password": new_password},
        )
        assert new_login.status_code == 200
        new_token = new_login.json()["access_token"]

        # Access protected route with new token
        profile_response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {new_token}"},
        )
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == original_email


class TestRefreshToken:
    """Test refresh token endpoint."""

    def test_refresh_token_success(self, client, test_user, test_user_data):
        """
        Test successful token refresh.

        Should return 200 OK with new access token.
        """
        # Get tokens from login
        login_response = client.post(
            "/users/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        refresh_token = tokens.get("refresh_token")

        # Should have refresh token in response
        assert refresh_token is not None
        assert len(refresh_token) > 0

        # Use refresh token to get new access token
        refresh_response = client.post(
            "/users/refresh-token",
            json={"refresh_token": refresh_token},
        )

        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert len(new_tokens["access_token"]) > 0

    def test_refresh_token_invalid(self, client):
        """
        Test refresh with invalid token.

        Should return 401 Unauthorized.
        """
        response = client.post(
            "/users/refresh-token",
            json={"refresh_token": "invalid.refresh.token"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_refresh_token_missing(self, client):
        """
        Test refresh without providing refresh token.

        Should return 422 Unprocessable Entity.
        """
        response = client.post(
            "/users/refresh-token",
            json={},
        )

        assert response.status_code == 422

    def test_refresh_token_enables_new_requests(
        self, client, test_user, test_user_data
    ):
        """
        Test that refreshed token can be used to access protected endpoints.
        """
        # Login
        login_response = client.post(
            "/users/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        tokens = login_response.json()
        refresh_token = tokens.get("refresh_token")

        # Refresh token
        refresh_response = client.post(
            "/users/refresh-token",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json()["access_token"]

        # Use new access token to access protected endpoint
        protected_response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )

        assert protected_response.status_code == 200
        data = protected_response.json()
        assert data["email"] == test_user_data["email"]

    def test_refresh_token_different_from_access_token(
        self, client, test_user, test_user_data
    ):
        """
        Test that refresh token is different from access token.
        """
        login_response = client.post(
            "/users/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")

        # Should be different tokens
        assert access_token != refresh_token
        # Refresh token should be longer (64 char hex from secrets.token_hex)
        assert len(refresh_token) > len(access_token.split(".")[0])

    def test_refresh_token_returns_new_access_token(
        self, client, test_user, test_user_data
    ):
        """
        Test that refresh returns a valid new access token.
        """
        # Login
        login_response = client.post(
            "/users/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        refresh_token = login_response.json().get("refresh_token")

        # Refresh
        refresh = client.post(
            "/users/refresh-token",
            json={"refresh_token": refresh_token},
        )
        assert refresh.status_code == 200
        token = refresh.json()["access_token"]

        # Use refreshed token to access protected endpoint
        profile_response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == test_user_data["email"]
