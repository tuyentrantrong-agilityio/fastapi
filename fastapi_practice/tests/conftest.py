"""
Pytest configuration and shared fixtures for all tests.

This module provides fixtures for:
- FastAPI test client
- Test database
- Test user creation and authentication
- Async database session for unit testing
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from datetime import timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import insert

from app.main import app
from app.core.security import create_access_token
from app.core.hashing import hash_password
from app.db.base import SQLModel
from app.db.session import get_async_session
from app.models.user import User


@pytest_asyncio.fixture
async def async_engine():
    """Create an async engine for testing (function-scoped per test).

    Uses SQLite file (test_app.db) instead of in-memory for better
    test isolation and persistence. Database is reset between tests.
    """
    import os

    # Use SQLite file in project root
    db_file = "test_app.db"
    db_url = f"sqlite+aiosqlite:///./{db_file}"

    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup: drop all tables and close engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()

    # Delete test database file
    if os.path.exists(db_file):
        os.remove(db_file)


@pytest_asyncio.fixture
async def async_session(async_engine):
    """
    Provide an async database session for unit testing.

    Creates an in-memory SQLite database, initializes tables,
    yields the session, then cleans up.

    Usage:
        async def test_something(async_session: AsyncSession):
            ...
    """
    # Create async session factory
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # Yield session
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def client(async_engine):
    """
    Provide a FastAPI test client with async database override.

    Returns:
        TestClient: FastAPI test client for making HTTP requests
    """

    def override_get_async_session_factory():
        async def override_get_async_session():
            async_session_maker = async_sessionmaker(
                async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
            async with async_session_maker() as session:
                yield session

        return override_get_async_session

    app.dependency_overrides[get_async_session] = override_get_async_session_factory()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """
    Provide test user credentials.

    Returns:
        dict: User data with email and password
    """
    return {
        "email": "testuser@example.com",
        "password": "pass1234",
    }


@pytest_asyncio.fixture
async def test_user(test_user_data, async_session):
    """
    Create a test user in the async database.

    Args:
        test_user_data: User credentials fixture
        async_session: Async database session

    Returns:
        User: Created user object
    """
    from app.services.user_service import create_user_service
    from app.schemas.user import UserCreate

    user_create = UserCreate(
        email=test_user_data["email"],
        password=test_user_data["password"],
    )
    user = await create_user_service(
        session=async_session,
        user=user_create,
    )

    await async_session.commit()
    await async_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def test_admin_user(async_session):
    """
    Create a test admin user in the async database.

    Args:
        async_session: Async database session

    Returns:
        User: Created admin user object
    """
    from app.services.user_service import create_user_service
    from app.schemas.user import UserCreate

    admin_create = UserCreate(
        email="admin@example.com",
        password="admin123",
    )
    admin = await create_user_service(
        session=async_session,
        user=admin_create,
    )

    # Set role to admin
    admin.role = "admin"

    await async_session.commit()
    await async_session.refresh(admin)

    return admin


@pytest.fixture
def user_token(test_user):
    """
    Generate a valid JWT token for test user.

    Args:
        test_user: Test user fixture

    Returns:
        str: Valid JWT token
    """
    access_token_expires = timedelta(minutes=30)
    token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=access_token_expires,
    )
    return token


@pytest.fixture
def admin_token(test_admin_user):
    """
    Generate a valid JWT token for admin user.

    Args:
        test_admin_user: Test admin user fixture

    Returns:
        str: Valid JWT token for admin
    """
    access_token_expires = timedelta(minutes=30)
    token = create_access_token(
        data={"sub": test_admin_user.email},
        expires_delta=access_token_expires,
    )
    return token


@pytest.fixture
def auth_headers(user_token):
    """
    Provide Authorization header with Bearer token.

    Args:
        user_token: JWT token fixture

    Returns:
        dict: HTTP headers with Authorization
    """
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_auth_headers(admin_token):
    """
    Provide Authorization header with admin Bearer token.

    Args:
        admin_token: JWT admin token fixture

    Returns:
        dict: HTTP headers with admin Authorization
    """
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def test_user_2(async_session):
    """
    Create a second test user in the async database for authorization testing.

    Args:
        async_session: Async database session

    Returns:
        User: Created user object
    """
    from app.services.user_service import create_user_service
    from app.schemas.user import UserCreate

    user_create = UserCreate(
        email="testuser2@example.com",
        password="pass5678",
    )
    user = await create_user_service(
        session=async_session,
        user=user_create,
    )

    await async_session.commit()
    await async_session.refresh(user)

    return user


@pytest.fixture
def user_token_2(test_user_2):
    """
    Generate a valid JWT token for second test user.

    Args:
        test_user_2: Second test user fixture

    Returns:
        str: Valid JWT token for user 2
    """
    access_token_expires = timedelta(minutes=30)
    token = create_access_token(
        data={"sub": test_user_2.email},
        expires_delta=access_token_expires,
    )
    return token


@pytest.fixture
def auth_headers_user_2(user_token_2):
    """
    Provide Authorization header with Bearer token for second user.

    Args:
        user_token_2: JWT token fixture for user 2

    Returns:
        dict: HTTP headers with Authorization for user 2
    """
    return {"Authorization": f"Bearer {user_token_2}"}
