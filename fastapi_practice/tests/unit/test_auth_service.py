import pytest
from unittest.mock import patch, AsyncMock
from app.core.exceptions import UnauthorizedException
from app.services.auth_service import login_service, refresh_access_token_service


class TestLoginService:
    """Unit tests for login_service function"""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login returns user data with tokens"""
        # Setup: Mock data
        mock_user_data = {
            "id": 1,
            "email": "user@test.com",
            "full_name": "Test User",
            "is_admin": False,
            "hashed_password": "$2b$12$hashedpassword123",
        }

        # Mock: get_user_by_email_service and token generation
        with (
            patch(
                "app.services.auth_service.get_user_by_email_service",
                new_callable=AsyncMock,
            ) as mock_get_user,
            #             patch(
            #     "app.services.auth_service.get_user_by_email_service",
            #     new=AsyncMock(return_value=mock_user_data)  # ← AsyncMock + return_value
            # )
            patch("app.services.auth_service.verify_password", return_value=True),
            patch(
                "app.services.auth_service.create_access_token",
                return_value="fake_access_token_123",
            ),
            patch(
                "app.services.auth_service.generate_refresh_token",
                return_value="fake_refresh_token_456",
            ),
            patch(
                "app.services.auth_service.hash_refresh_token",
                return_value="hashed_token_456",
            ),
            patch("app.services.auth_service.refresh_tokens_db", {}),
        ):
            mock_get_user.return_value = mock_user_data

            # Act: Call login_service
            result = await login_service("user@test.com", "password123")

            # Assert: Verify result structure
            assert result["access_token"] == "fake_access_token_123"
            assert result["refresh_token"] == "fake_refresh_token_456"
            assert result["token_type"] == "bearer"

            # Assert: Verify get_user was called
            mock_get_user.assert_called_once_with("user@test.com")

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        """Test login with non-existent email raises UnauthorizedException"""
        # Mock: User not found
        with patch(
            "app.services.auth_service.get_user_by_email_service",
            new_callable=AsyncMock,
        ) as mock_get_user:
            mock_get_user.return_value = None

            # Act & Assert: Should raise UnauthorizedException
            with pytest.raises(
                UnauthorizedException, match="Invalid email or password"
            ):
                await login_service("nonexistent@test.com", "password123")

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Test login with wrong password raises UnauthorizedException"""
        # Setup: Mock user data
        mock_user_data = {
            "id": 1,
            "email": "user@test.com",
            "full_name": "Test User",
            "hashed_password": "$2b$12$hashedpassword123",
        }

        # Mock: User found but password verification fails
        with (
            patch(
                "app.services.auth_service.get_user_by_email_service",
                new_callable=AsyncMock,
            ) as mock_get_user,
            patch("app.services.auth_service.verify_password", return_value=False),
        ):
            mock_get_user.return_value = mock_user_data

            # Act & Assert: Should raise UnauthorizedException
            with pytest.raises(
                UnauthorizedException, match="Invalid email or password"
            ):
                await login_service("user@test.com", "wrongpassword")

    @pytest.mark.asyncio
    async def test_login_stores_refresh_token(self):
        """Test that login stores hashed refresh token in database"""
        # Setup: Mock data and database
        mock_user_data = {
            "id": 1,
            "email": "user@test.com",
            "hashed_password": "hash123",
        }
        mock_refresh_tokens_db = {}

        # Mock: Token generation and storage
        with (
            patch(
                "app.services.auth_service.get_user_by_email_service",
                new_callable=AsyncMock,
            ) as mock_get_user,
            patch("app.services.auth_service.verify_password", return_value=True),
            patch(
                "app.services.auth_service.create_access_token",
                return_value="access_token",
            ),
            patch(
                "app.services.auth_service.generate_refresh_token",
                return_value="refresh_token",
            ),
            patch(
                "app.services.auth_service.hash_refresh_token",
                return_value="hashed_token",
            ),
            patch(
                "app.services.auth_service.refresh_tokens_db", mock_refresh_tokens_db
            ),
        ):
            mock_get_user.return_value = mock_user_data

            # Act: Call login_service
            await login_service("user@test.com", "password123")

            # Assert: Verify token was stored
            assert "hashed_token" in mock_refresh_tokens_db
            assert mock_refresh_tokens_db["hashed_token"]["user_id"] == 1


class TestRefreshAccessTokenService:
    """Unit tests for refresh_access_token_service function"""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Test successful refresh token generates new access and refresh tokens"""
        # Setup: Import datetime and create mock database
        import datetime

        mock_user_data = {"id": 1, "email": "user@test.com"}
        mock_refresh_tokens_db = {
            "hashed_old_token": {
                "user_id": 1,
                "expires_at": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=7),
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
        }
        mock_users_db = {1: mock_user_data}

        # Mock: Token operations
        with (
            patch(
                "app.services.auth_service.hash_refresh_token",
                return_value="hashed_old_token",
            ),
            patch(
                "app.services.auth_service.refresh_tokens_db", mock_refresh_tokens_db
            ),
            patch("app.services.auth_service.users_db", mock_users_db),
            patch(
                "app.services.auth_service.create_access_token",
                return_value="new_access_token",
            ),
            patch(
                "app.services.auth_service.generate_refresh_token",
                return_value="new_refresh_token",
            ),
        ):
            # Act: Call refresh_access_token_service
            result = await refresh_access_token_service("old_refresh_token")

            # Assert: Verify new tokens were generated
            assert result["access_token"] == "new_access_token"
            assert result["refresh_token"] == "new_refresh_token"
            assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self):
        """Test refresh with invalid token raises UnauthorizedException"""
        # Setup: Empty token database
        mock_refresh_tokens_db = {}

        # Mock: Token not found
        with (
            patch(
                "app.services.auth_service.hash_refresh_token",
                return_value="hashed_invalid_token",
            ),
            patch(
                "app.services.auth_service.refresh_tokens_db", mock_refresh_tokens_db
            ),
        ):
            # Act & Assert: Should raise exception
            with pytest.raises(
                UnauthorizedException, match="Invalid or expired refresh token"
            ):
                await refresh_access_token_service("invalid_token")

    @pytest.mark.asyncio
    async def test_refresh_token_expired(self):
        """Test refresh with expired token raises UnauthorizedException"""
        # Setup: Mock expired token
        import datetime

        mock_refresh_tokens_db = {
            "hashed_expired_token": {
                "user_id": 1,
                "expires_at": datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(days=1),  # Expired
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
        }

        # Mock: Token verification
        with (
            patch(
                "app.services.auth_service.hash_refresh_token",
                return_value="hashed_expired_token",
            ),
            patch(
                "app.services.auth_service.refresh_tokens_db", mock_refresh_tokens_db
            ),
        ):
            # Act & Assert: Should raise exception
            with pytest.raises(
                UnauthorizedException, match="Refresh token has expired"
            ):
                await refresh_access_token_service("expired_token")

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_found(self):
        """Test refresh token when user not found raises UnauthorizedException"""
        # Setup: Token exists but user deleted
        import datetime

        mock_refresh_tokens_db = {
            "hashed_token": {
                "user_id": 999,  # Non-existent user
                "expires_at": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=7),
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
        }
        mock_users_db = {}  # No users

        # Mock: Token found but user not found
        with (
            patch(
                "app.services.auth_service.hash_refresh_token",
                return_value="hashed_token",
            ),
            patch(
                "app.services.auth_service.refresh_tokens_db", mock_refresh_tokens_db
            ),
            patch("app.services.auth_service.users_db", mock_users_db),
        ):
            # Act & Assert: Should raise exception
            with pytest.raises(UnauthorizedException, match="User not found"):
                await refresh_access_token_service("valid_token")

    @pytest.mark.asyncio
    async def test_refresh_token_revokes_old_token(self):
        """Test that refresh deletes old token from database"""
        # Setup: Mock database
        import datetime

        mock_user_data = {"id": 1, "email": "user@test.com"}
        mock_refresh_tokens_db = {
            "hashed_old_token": {
                "user_id": 1,
                "expires_at": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=7),
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
        }
        mock_users_db = {1: mock_user_data}

        # Mock: All token operations
        with (
            patch(
                "app.services.auth_service.hash_refresh_token",
                side_effect=["hashed_old_token", "hashed_new_token"],
            ),
            patch(
                "app.services.auth_service.refresh_tokens_db", mock_refresh_tokens_db
            ),
            patch("app.services.auth_service.users_db", mock_users_db),
            patch(
                "app.services.auth_service.create_access_token",
                return_value="new_access_token",
            ),
            patch(
                "app.services.auth_service.generate_refresh_token",
                return_value="new_refresh_token",
            ),
        ):
            # Act: Call refresh_access_token_service
            await refresh_access_token_service("old_refresh_token")

            # Assert: Old token should be deleted (revoked)
            assert "hashed_old_token" not in mock_refresh_tokens_db
            # Assert: New token should be added
            assert "hashed_new_token" in mock_refresh_tokens_db
