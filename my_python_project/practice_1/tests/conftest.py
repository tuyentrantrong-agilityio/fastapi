"""
Pytest configuration and shared fixtures for all tests.

This module provides fixtures for:
- FastAPI test client
- Test database reset
- Test user creation and authentication
"""

import pytest
from fastapi.testclient import TestClient
from datetime import timedelta

from main import app
from core.security import create_access_token
from core.hashing import hash_password
from db.storage import (
    users_db,
    tasks_db,
    projects_db,
    user_id_counter,
    task_id_counter,
    project_id_counter,
)


@pytest.fixture
def client():
    """
    Provide a FastAPI test client.

    Returns:
        TestClient: FastAPI test client for making HTTP requests
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """
    Reset database before each test.

    Clears all data from users_db, tasks_db, projects_db and resets ID counters.
    This fixture runs automatically before every test to ensure clean state.
    """
    users_db.clear()
    tasks_db.clear()
    projects_db.clear()
    user_id_counter["id"] = 1
    task_id_counter["id"] = 1
    project_id_counter["id"] = 1
    yield


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


@pytest.fixture
def test_user(test_user_data):
    """
    Create a test user in the database.

    Args:
        test_user_data: User credentials fixture

    Returns:
        dict: Created user data with id, email, hashed_password, role
    """
    user_id = user_id_counter["id"]
    user_id_counter["id"] += 1

    users_db[user_id] = {
        "id": user_id,
        "email": test_user_data["email"],
        "hashed_password": hash_password(test_user_data["password"]),
        "is_active": True,
        "role": "user",
    }

    return users_db[user_id]


@pytest.fixture
def test_admin_user():
    """
    Create a test admin user in the database.

    Returns:
        dict: Created admin user data
    """
    user_id = user_id_counter["id"]
    user_id_counter["id"] += 1

    users_db[user_id] = {
        "id": user_id,
        "email": "admin@example.com",
        "hashed_password": hash_password("admin123"),
        "is_active": True,
        "role": "admin",
    }

    return users_db[user_id]


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
        data={"sub": test_user["email"]},
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
        data={"sub": test_admin_user["email"]},
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
