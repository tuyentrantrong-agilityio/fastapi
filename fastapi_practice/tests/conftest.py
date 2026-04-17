"""
Pytest configuration and shared fixtures for all tests.

This module provides fixtures for:
- FastAPI test client
- Test database
- Test user creation and authentication
- Async database session for unit testing
- Celery + Redis mocking for background tasks
- Test markers (unit, integration)
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from datetime import timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import insert
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.core.security import create_access_token
from app.core.hashing import hash_password
from app.db.base import SQLModel
from app.db.session import get_async_session
from app.models.user import User


def pytest_configure(config):
    """Register custom pytest markers for test classification."""
    config.addinivalue_line("markers", "unit: mark test as a unit test (mocked, fast)")
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (real DB, slower)"
    )


@pytest.fixture(autouse=True)
def mock_celery_tasks(request, monkeypatch):
    """Auto-use fixture to mock all Celery tasks to prevent Redis connection attempts.

    Skips mocking for unit tests (which need to test real task attributes).
    Only mocks for integration tests.
    """
    # Skip mocking for unit tests - they need real Celery task objects
    if "unit" in [marker.name for marker in request.node.iter_markers()]:
        return

    from unittest.mock import MagicMock
    from app.tasks import email_tasks, task_tasks

    # Create mocks that return immediately (Mock objects are callable and return another Mock)
    mock_send_welcome = MagicMock()
    mock_send_task_assigned = MagicMock()
    mock_process_task = MagicMock()

    # Patch the task objects in their modules
    monkeypatch.setattr(email_tasks, "send_welcome_email_task", mock_send_welcome)
    monkeypatch.setattr(
        email_tasks, "send_task_assigned_email_task", mock_send_task_assigned
    )
    monkeypatch.setattr(task_tasks, "process_task_async", mock_process_task)


@pytest.fixture
def async_engine():
    """Create an async engine for testing with in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
    return engine


@pytest_asyncio.fixture
async def async_session(async_engine):
    """
    Provide an async database session for unit testing.

    Creates tables, yields the session, then cleans up.

    Usage:
        async def test_something(async_session: AsyncSession):
            ...
    """
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

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

    # Cleanup: drop all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


@pytest.fixture
def client(async_engine):
    """
    Provide a FastAPI test client with async database override.

    Returns:
        TestClient: FastAPI test client for making HTTP requests
    """

    # Create tables synchronously
    import asyncio

    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_tables())
    loop.close()

    # Setup dependency override
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
    test_client = TestClient(app)
    yield test_client
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


# ========== CELERY + REDIS MOCKING ==========


@pytest.fixture
def celery_config(monkeypatch):
    """Configure Celery for testing with eager mode.

    In eager mode, tasks are executed synchronously (not queued),
    making it easy to test task logic without a running worker.
    """
    monkeypatch.setenv("CELERY_ALWAYS_EAGER", "True")
    monkeypatch.setenv("CELERY_EAGER_PROPAGATES_EXCEPTIONS", "True")
    return {
        "task_always_eager": True,
        "task_eager_propagates": True,
    }


@pytest.fixture
def mock_redis_client(mocker):
    """Provide a mocked Redis client for testing.

    Uses AsyncMock (not Mock) to properly handle async operations.
    Patch location: where redis_client is USED, not where it's defined.

    Example usage in test:
        mock_redis = mock_redis_client
        r1 = client.get("/tasks/1")
        assert r1.headers.get("X-Cache") in ["MISS", None]
    """
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.exists = AsyncMock(return_value=0)
    mock.ttl = AsyncMock(return_value=-2)

    return mocker.patch("app.services.cache.redis_client", mock)


@pytest.fixture
def invalid_auth_headers():
    """Provide invalid Authorization header for auth failure testing.

    Returns:
        dict: HTTP headers with invalid Bearer token
    """
    return {"Authorization": "Bearer invalid_token_xyz"}


# ========== TASK FIXTURES FOR TESTING ==========


@pytest_asyncio.fixture
async def test_project(async_session, test_user):
    """Create a test project for the test user.

    Args:
        async_session: Async database session
        test_user: Test user fixture

    Returns:
        Project: Created project object
    """
    from app.models.project import Project

    project = Project(
        name="Test Project",
        description="A test project",
        user_id=test_user.id,
    )
    async_session.add(project)
    await async_session.commit()
    await async_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_task(async_session, test_user, test_project):
    """Create a test task for the test user.

    Args:
        async_session: Async database session
        test_user: Test user fixture
        test_project: Test project fixture

    Returns:
        Task: Created task object
    """
    from app.models.task import Task

    task = Task(
        title="Test Task",
        description="A test task",
        status="todo",
        user_id=test_user.id,
        project_id=test_project.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task
