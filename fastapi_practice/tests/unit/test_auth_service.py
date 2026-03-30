"""Unit tests for auth service functions with mocked AsyncSession."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.services.auth_service import login_service, refresh_access_token_service
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.exceptions import UnauthorizedException


def make_user(id=1, email="user@test.com", hashed_password="hash_pwd_123", role="user"):
    """Helper to create User model instance."""
    user = User(
        id=id,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )
    return user


def make_refresh_token(id=1, user_id=1, token_hash="hash_123", expires_at=None):
    """Helper to create RefreshToken model instance."""
    if expires_at is None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    token = RefreshToken(
        id=id,
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        is_revoked=False,
    )
    return token


class TestLoginService:
    """Test cases for login_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful login returns user data with tokens."""

        # --- Mock session and user database ---
        session = AsyncMock(spec=AsyncSession)
        user = make_user(id=1, email="user@test.com")

        # --- Mock all auth service dependencies (email lookup, password verify, token generation) ---
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
                return_value="fake_access_token",
            ),
            patch(
                "app.services.auth_service.generate_refresh_token",
                return_value="fake_refresh_token",
            ),
            patch(
                "app.services.auth_service.hash_refresh_token",
                return_value="hashed_token_hash",
            ),
        ):
            # --- Configure mocks to return valid user ---
            mock_get_user.return_value = user
            session.add = MagicMock()
            session.commit = AsyncMock()

            # --- Call the service function under test ---
            result = await login_service(session, "user@test.com", "password123")

            # --- Assert correct tokens returned and dependencies called ---
            assert result["access_token"] == "fake_access_token"
            assert result["refresh_token"] == "fake_refresh_token"
            assert result["token_type"] == "bearer"
            mock_get_user.assert_awaited_once()  # User lookup called
            session.add.assert_called_once()  # Refresh token stored

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        """Test login with non-existent email raises UnauthorizedException."""

        # --- Mock session ---
        session = AsyncMock(spec=AsyncSession)

        # --- Mock user lookup to return None (user doesn't exist) ---
        with patch(
            "app.services.auth_service.get_user_by_email_service",
            new_callable=AsyncMock,
        ) as mock_get_user:
            mock_get_user.return_value = None  # Simulate: user not found

            # --- Call and verify exception is raised ---
            with pytest.raises(
                UnauthorizedException, match="Invalid email or password"
            ):
                await login_service(session, "nonexistent@test.com", "password123")

            # --- Assert user lookup was attempted ---
            mock_get_user.assert_awaited_once()  # Service tried to find user

    @pytest.mark.asyncio
    async def test_wrong_password(self):
        """Test login with wrong password raises UnauthorizedException."""

        # --- Mock session and user ---
        session = AsyncMock(spec=AsyncSession)
        user = make_user(id=1, email="user@test.com")

        # --- Mock user lookup (found) but password verification fails ---
        with (
            patch(
                "app.services.auth_service.get_user_by_email_service",
                new_callable=AsyncMock,
            ) as mock_get_user,
            patch("app.services.auth_service.verify_password", return_value=False),
        ):
            # --- Configure mocks ---
            mock_get_user.return_value = user  # User found

            # --- Call and verify exception is raised ---
            with pytest.raises(
                UnauthorizedException, match="Invalid email or password"
            ):
                await login_service(session, "user@test.com", "wrongpassword")

            # --- Assert user lookup was attempted before password check ---
            mock_get_user.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stores_refresh_token(self):
        """Test that login stores refresh token record."""

        # --- Mock session and user ---
        session = AsyncMock(spec=AsyncSession)
        user = make_user(id=1, email="user@test.com")

        # --- Mock all auth dependencies for successful login ---
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
        ):
            # --- Configure mocks and DB operations ---
            mock_get_user.return_value = user
            session.add = MagicMock()
            session.commit = AsyncMock()

            # --- Call the service function under test ---
            result = await login_service(session, "user@test.com", "password123")

            # --- Assert tokens returned and refresh token was stored ---
            assert result["access_token"] == "access_token"
            assert result["refresh_token"] == "refresh_token"
            session.add.assert_called_once()  # Refresh token added to session
            session.commit.assert_awaited_once()  # Changes committed to DB


class TestRefreshAccessTokenService:
    """Test cases for refresh_access_token_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful refresh token generates new tokens."""

        # --- Mock session, user, and existing valid refresh token ---
        session = AsyncMock(spec=AsyncSession)
        user = make_user(id=1, email="user@test.com")
        old_token = make_refresh_token(id=1, user_id=1, token_hash="old_hash")

        # --- Mock token lookup query (find existing refresh token) ---
        query_result = MagicMock()
        session.execute.return_value = query_result
        query_result.scalars.return_value.first.return_value = (
            old_token  # Simulate: token found
        )
        session.delete = AsyncMock()
        session.commit = AsyncMock()

        # --- Mock cryptography and token generation ---
        with (
            patch(
                "app.services.auth_service.hash_refresh_token", return_value="old_hash"
            ),
            patch(
                "app.services.auth_service.create_access_token",
                return_value="new_access_token",
            ),
            patch(
                "app.services.auth_service.generate_refresh_token",
                return_value="new_refresh_token",
            ),
        ):
            # --- Configure token's user relationship ---
            old_token.user = user

            # --- Call the service function under test ---
            result = await refresh_access_token_service(session, "old_refresh_token")

            # --- Assert new tokens returned and old token replaced ---
            assert result["access_token"] == "new_access_token"
            assert result["refresh_token"] == "new_refresh_token"
            assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """Test refresh with invalid token raises UnauthorizedException."""

        # --- Mock session with no token found ---
        session = AsyncMock(spec=AsyncSession)
        query_result = MagicMock()
        session.execute.return_value = query_result
        query_result.scalars.return_value.first.return_value = (
            None  # Simulate: token not found
        )

        # --- Mock token hashing (invalid result) ---
        with patch(
            "app.services.auth_service.hash_refresh_token", return_value="invalid_hash"
        ):
            # --- Call and verify exception is raised ---
            with pytest.raises(
                UnauthorizedException, match="Invalid or expired refresh token"
            ):
                await refresh_access_token_service(session, "invalid_token")

    @pytest.mark.asyncio
    async def test_expired_token(self):
        """Test refresh with expired token raises UnauthorizedException."""

        # --- Mock session and expired refresh token ---
        session = AsyncMock(spec=AsyncSession)

        # --- Create token with past expiration date ---
        expired_token = make_refresh_token(
            id=1,
            user_id=1,
            token_hash="expired_hash",
            expires_at=datetime.now(timezone.utc)
            - timedelta(days=1),  # Expired 1 day ago
        )

        # --- Mock token lookup query (find expired token) ---
        query_result = MagicMock()
        session.execute.return_value = query_result
        query_result.scalars.return_value.first.return_value = (
            expired_token  # Token found but expired
        )
        session.delete = AsyncMock()
        session.commit = AsyncMock()

        # --- Mock token hashing ---
        with patch(
            "app.services.auth_service.hash_refresh_token", return_value="expired_hash"
        ):
            # --- Call and verify exception is raised ---
            with pytest.raises(
                UnauthorizedException, match="Refresh token has expired"
            ):
                await refresh_access_token_service(session, "expired_token")

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        """Test refresh token when user not found raises UnauthorizedException."""

        # --- Mock session and refresh token without user ---
        session = AsyncMock(spec=AsyncSession)

        # --- Create token for non-existent user ---
        token = make_refresh_token(id=1, user_id=999)  # User ID doesn't exist
        token.user = None  # Simulate: user relationship not loaded/not found

        # --- Mock token lookup query (token found but user missing) ---
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = token
        session.execute.return_value = query_result

        # --- Mock token hashing ---
        with patch(
            "app.services.auth_service.hash_refresh_token", return_value="token_hash"
        ):
            # --- Call and verify exception is raised ---
            with pytest.raises(UnauthorizedException, match="User not found"):
                await refresh_access_token_service(session, "valid_token")
