"""Unit tests for user service functions with mocked AsyncSession."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import (
    create_user_service,
    get_user_by_email_service,
    update_user_profile_service,
)


def make_user(id=1, email="test@example.com", hashed_password="hash_pwd_123", role="user"):
    """Helper to create User model instance."""
    user = User(
        id=id,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )
    return user


class TestCreateUserService:
    """Test cases for create_user_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Should successfully create new user."""

        # --- Mock session and database query (no existing user with this email) ---
        session = AsyncMock(spec=AsyncSession)
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = None  # Simulate: email not found
        session.execute.return_value = query_result

        # --- Mock DB operations (add, commit, refresh) ---
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        def side_effect_refresh(user):
            user.id = 1  # Simulate: database assigns new ID

        session.refresh.side_effect = side_effect_refresh

        # --- Prepare input DTO ---
        user_create = UserCreate(email="newuser@example.com", password="password123")

        # --- Call the service function under test ---
        result = await create_user_service(session, user_create)

        # --- Assert correct behavior and DB calls ---
        session.execute.assert_awaited_once()  # Check query was executed
        session.add.assert_called_once()  # User added to session
        session.commit.assert_awaited_once()  # Changes committed
        session.refresh.assert_awaited_once()  # User refreshed with DB-assigned ID
        assert result.email == "newuser@example.com"
        assert result.role == "user"

    @pytest.mark.asyncio
    async def test_duplicate_email(self):
        """Should raise error if email already exists."""

        # --- Mock session and simulated existing user in database ---
        session = AsyncMock(spec=AsyncSession)
        existing_user = make_user(id=1, email="existing@example.com")
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = (
            existing_user  # Simulate: user exists
        )
        session.execute.return_value = query_result

        # --- Prepare input DTO with duplicate email ---
        user_create = UserCreate(email="existing@example.com", password="password123")

        # --- Call and verify exception is raised ---
        with pytest.raises(BadRequestException, match="Email already registered"):
            await create_user_service(session, user_create)

        # --- Assert service stopped before DB modifications ---
        session.execute.assert_awaited_once()  # Only query executed
        session.add.assert_not_called()  # No user added (error thrown)


class TestGetUserByEmailService:
    """Test cases for get_user_by_email_service."""

    @pytest.mark.asyncio
    async def test_found(self):
        """Should return user if email exists."""

        # --- Mock session and simulated user in database ---
        session = AsyncMock(spec=AsyncSession)
        found_user = make_user(id=1, email="user@example.com")
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = found_user  # Simulate: user found
        session.execute.return_value = query_result

        # --- Call the service function under test ---
        result = await get_user_by_email_service(session, "user@example.com")

        # --- Assert correct database query and result ---
        session.execute.assert_awaited_once()  # Query executed
        assert result == found_user  # Correct user returned
        assert result.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_not_found(self):
        """Should return None if email not exists."""

        # --- Mock session with no user found ---
        session = AsyncMock(spec=AsyncSession)
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = None  # Simulate: no user found
        session.execute.return_value = query_result

        # --- Call the service function under test ---
        result = await get_user_by_email_service(session, "nonexistent@example.com")

        # --- Assert query executed and None returned ---
        session.execute.assert_awaited_once()  # Query executed
        assert result is None  # No user found returns None


class TestUpdateUserProfileService:
    """Test cases for update_user_profile_service."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Should successfully update user profile if email is unique and user exists."""

        # --- Mock session and database user ---
        session = AsyncMock(spec=AsyncSession)
        existing_user = make_user(id=1, email="user@example.com", role="user")
        session.get.return_value = existing_user  # session.get() will return our test user

        # --- Mock DB operations (add, commit, refresh) ---
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Mock check for duplicate email (simulate no other user with same email) ---
        mock_execute_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None  # Simulate: no user found with this email
        mock_execute_result.scalars.return_value = mock_scalars
        session.execute.return_value = mock_execute_result

        # --- Prepare input DTO for user update ---
        user_update = UserUpdate(email="newemail@example.com")

        # --- Call the service function under test ---
        result = await update_user_profile_service(session, 1, user_update, is_admin=False)

        # --- Assert correct behavior and DB calls ---
        session.get.assert_awaited_once_with(User, 1)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once()
        assert result.email == "newemail@example.com"

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        """Should raise NotFoundException if user not found."""

        # --- Mock session with no user found ---
        session = AsyncMock(spec=AsyncSession)
        session.get.return_value = None  # Simulate: user doesn't exist

        # --- Prepare input DTO ---
        user_update = UserUpdate(email="new@example.com")

        # --- Call and verify exception is raised ---
        with pytest.raises(NotFoundException, match="User not found"):
            await update_user_profile_service(session, 999, user_update, is_admin=False)

        # --- Assert service attempted to fetch user ---
        session.get.assert_awaited_once_with(User, 999)  # Lookup attempted for user ID 999

    @pytest.mark.asyncio
    async def test_duplicate_email(self):
        """Should raise error if new email already taken."""

        # --- Mock session and existing user ---
        session = AsyncMock(spec=AsyncSession)
        existing_user = make_user(id=1, email="user@example.com")
        session.get.return_value = existing_user  # User to update

        # --- Mock query showing another user already has the target email ---
        other_user = make_user(id=2, email="taken@example.com")
        query_result = MagicMock()
        query_result.scalars.return_value.first.return_value = other_user  # Simulate: email taken
        session.execute.return_value = query_result

        # --- Prepare input DTO with duplicate email ---
        user_update = UserUpdate(email="taken@example.com")

        # --- Call and verify exception is raised ---
        with pytest.raises(BadRequestException, match="Email already taken"):
            await update_user_profile_service(session, 1, user_update, is_admin=False)

    @pytest.mark.asyncio
    async def test_admin_change_role(self):
        """Should allow admin to change user role."""

        # --- Mock session and existing user ---
        session = AsyncMock(spec=AsyncSession)
        existing_user = make_user(id=1, email="user@example.com", role="user")
        session.get.return_value = existing_user

        # --- Mock DB operations ---
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        # --- Prepare role update from admin user ---
        user_update = UserUpdate(role="admin")

        # --- Call the service function with admin=True ---
        result = await update_user_profile_service(session, 1, user_update, is_admin=True)

        # --- Assert role was successfully updated ---
        assert result.role == "admin"  # Role changed
        session.commit.assert_awaited_once()  # Changes committed

    @pytest.mark.asyncio
    async def test_non_admin_cannot_change_role(self):
        """Should forbid non-admin from changing role."""

        # --- Mock session and existing user ---
        session = AsyncMock(spec=AsyncSession)
        existing_user = make_user(id=1, email="user@example.com", role="user")
        session.get.return_value = existing_user

        # --- Prepare role update attempt by non-admin ---
        user_update = UserUpdate(role="admin")

        # --- Call with is_admin=False and verify exception is raised ---
        with pytest.raises(ForbiddenException, match="Only admin users can change roles"):
            await update_user_profile_service(session, 1, user_update, is_admin=False)
