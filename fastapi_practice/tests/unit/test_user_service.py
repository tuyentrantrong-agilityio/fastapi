"""Unit tests for user service functions."""

import pytest
from unittest.mock import patch, MagicMock
from app.services.user_service import (
    create_user_service,
    get_user_by_email_service,
    update_user_profile_service,
)
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import BadRequestException, ForbiddenException


@pytest.fixture
def user_create_data():
    """Sample user creation data."""
    return UserCreate(
        email="test@example.com",
        password="testpassword123",
    )


@pytest.fixture
def sample_user():
    """Sample user from database."""
    return {
        "id": 1,
        "email": "test@example.com",
        "hashed_password": "$argon2id$v=19$m=65540,t=3,p=4$...",
        "is_active": True,
        "role": "user",
    }


class TestCreateUserService:
    """Test create_user_service function."""

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Should successfully create new user."""
        with (
            patch("app.services.user_service.users_db", {}),
            patch("app.services.user_service.user_id_counter", {"id": 1}),
            patch("app.services.user_service.hash_password", return_value="hashed_pwd"),
        ):
            user_create = UserCreate(
                email="newuser@example.com",
                password="password123",
            )

            result = await create_user_service(user_create)

            assert result["email"] == "newuser@example.com"
            assert result["role"] == "user"
            assert "id" in result
            assert "hashed_password" not in result

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self):
        """Should raise error if email already exists."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "existing@example.com",
                "hashed_password": "hash",
                "is_active": True,
                "role": "user",
            }
        }

        with (
            patch("app.services.user_service.users_db", mock_users_db),
            patch("app.services.user_service.user_id_counter", {"id": 2}),
        ):
            user_create = UserCreate(
                email="existing@example.com",
                password="password123",
            )

            with pytest.raises(BadRequestException) as exc_info:
                await create_user_service(user_create)

            assert "Email already registered" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_create_user_increments_id(self):
        """Should increment user ID counter."""
        mock_counter = {"id": 5}

        with (
            patch("app.services.user_service.users_db", {}),
            patch("app.services.user_service.user_id_counter", mock_counter),
            patch("app.services.user_service.hash_password", return_value="hashed"),
        ):
            user_create = UserCreate(
                email="test@example.com",
                password="password123",
            )

            await create_user_service(user_create)

            assert mock_counter["id"] == 6


class TestGetUserByEmailService:
    """Test get_user_by_email_service function."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self):
        """Should return user when email exists."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "test@example.com",
                "hashed_password": "hash",
                "is_active": True,
                "role": "user",
            }
        }

        with patch("app.services.user_service.users_db", mock_users_db):
            result = await get_user_by_email_service("test@example.com")

            assert result is not None
            assert result["email"] == "test@example.com"
            assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self):
        """Should return None when email doesn't exist."""
        with patch("app.services.user_service.users_db", {}):
            result = await get_user_by_email_service("nonexistent@example.com")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_case_sensitive(self):
        """Email lookup should work with exact case."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "Test@Example.com",
                "hashed_password": "hash",
                "is_active": True,
                "role": "user",
            }
        }

        with patch("app.services.user_service.users_db", mock_users_db):
            # Exact case should work
            result = await get_user_by_email_service("Test@Example.com")
            assert result is not None

            # Different case should not match
            result = await get_user_by_email_service("test@example.com")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_multiple_users(self):
        """Should find correct user among multiple users."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "user1@example.com",
                "hashed_password": "hash1",
                "is_active": True,
                "role": "user",
            },
            2: {
                "id": 2,
                "email": "user2@example.com",
                "hashed_password": "hash2",
                "is_active": True,
                "role": "user",
            },
            3: {
                "id": 3,
                "email": "user3@example.com",
                "hashed_password": "hash3",
                "is_active": True,
                "role": "admin",
            },
        }

        with patch("app.services.user_service.users_db", mock_users_db):
            result = await get_user_by_email_service("user2@example.com")

            assert result is not None
            assert result["id"] == 2
            assert result["email"] == "user2@example.com"
            assert result["role"] == "user"


class TestUpdateUserProfileService:
    """Test update_user_profile_service function."""

    @pytest.mark.asyncio
    async def test_update_user_email(self):
        """Should update user email."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "old@example.com",
                "hashed_password": "hash",
                "is_active": True,
                "role": "user",
            }
        }

        with patch("app.services.user_service.users_db", mock_users_db):
            update_data = UserUpdate(email="new@example.com")
            result = await update_user_profile_service(1, update_data, is_admin=False)

            assert result["email"] == "new@example.com"
            assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_update_user_password(self):
        """Should update user password."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "test@example.com",
                "hashed_password": "old_hash",
                "is_active": True,
                "role": "user",
            }
        }

        with (
            patch("app.services.user_service.users_db", mock_users_db),
            patch("app.services.user_service.hash_password", return_value="new_hash"),
        ):
            update_data = UserUpdate(password="newpassword123")
            result = await update_user_profile_service(1, update_data, is_admin=False)

            assert result["email"] == "test@example.com"
            assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email(self):
        """Should raise error if new email already exists."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "user1@example.com",
                "hashed_password": "hash",
                "is_active": True,
                "role": "user",
            },
            2: {
                "id": 2,
                "email": "user2@example.com",
                "hashed_password": "hash",
                "is_active": True,
                "role": "user",
            },
        }

        with patch("app.services.user_service.users_db", mock_users_db):
            update_data = UserUpdate(email="user2@example.com")

            with pytest.raises(BadRequestException):
                await update_user_profile_service(1, update_data, is_admin=False)

    @pytest.mark.asyncio
    async def test_update_user_not_found(self):
        """Should raise error if user not found."""
        with patch("app.services.user_service.users_db", {}):
            update_data = UserUpdate(email="new@example.com")

            with pytest.raises(KeyError):
                await update_user_profile_service(999, update_data, is_admin=False)

    @pytest.mark.asyncio
    async def test_update_user_role_requires_admin(self):
        """Should require admin to update role."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "user@example.com",
                "hashed_password": "hash",
                "is_active": True,
                "role": "user",
            }
        }

        with patch("app.services.user_service.users_db", mock_users_db):
            # Regular user (not admin) trying to change role
            update_data = UserUpdate(role="admin")

            with pytest.raises(ForbiddenException):
                await update_user_profile_service(1, update_data, is_admin=False)

    @pytest.mark.asyncio
    async def test_update_user_with_no_changes(self):
        """Should handle update with no fields."""
        mock_users_db = {
            1: {
                "id": 1,
                "email": "test@example.com",
                "hashed_password": "hash",
                "is_active": True,
                "role": "user",
            }
        }

        with patch("app.services.user_service.users_db", mock_users_db):
            update_data = UserUpdate()  # Empty update
            result = await update_user_profile_service(1, update_data, is_admin=False)

            # Should still return user data
            assert result["id"] == 1
            assert result["email"] == "test@example.com"
