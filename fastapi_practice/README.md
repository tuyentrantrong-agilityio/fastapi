# FastAPI Task Management Application

A comprehensive FastAPI learning project demonstrating user authentication, task CRUD operations, project management, and role-based access control. Features JWT-based authentication, Argon2id password hashing, task ownership enforcement, and 129 comprehensive tests (47 unit tests + 82 integration tests).

## Overview

This project builds a production-like task management API with:
- User authentication and authorization with JWT tokens and refresh token rotation
- Secure password hashing using Argon2id (OWASP recommended)
- Full CRUD operations for tasks with filtering, search, and pagination
- Role-based access control (user vs admin)
- Task ownership enforcement (users can only access their own tasks)
- Project management with task assignments
- **129 comprehensive tests** (47 unit tests + 82 integration tests)
- Modular architecture with clear separation of concerns

## Tech Stack

- **FastAPI** 0.128.0 - Fast, modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** 2.12.5 - Data validation and settings management
- **Argon2-cffi** - Secure password hashing
- **python-jose** - JWT token generation and validation
- **Pytest** 9.0.2 - Testing framework
- **httpx** 0.28.1 - Async HTTP client for testing
- **Python** 3.11+

## Installation

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11 or higher
- pip (Python package manager)

### Quick Start

#### 1. Clone Repository and Navigate

```bash
git clone <repository-url>
cd fastapi_practice
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Create Environment File

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file (optional - defaults are set in config.py):

```env
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
DEBUG=True
```

#### 5. Run Application

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload

# Option 2: Using run script (macOS/Linux)
./run.sh

# Option 3: Windows batch file
run.bat
```

#### 6. Access Application

- API Documentation (Swagger UI): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

## Project Structure

```
fastapi_practice/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app setup and configuration
│   │
│   ├── core/                    # Core utilities and configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Settings and environment variables
│   │   ├── hashing.py           # Password hashing using Argon2id
│   │   ├── security.py          # JWT token generation and verification
│   │   ├── exceptions.py        # Custom exception classes
│   │   └── handlers.py          # Global exception handlers
│   │
│   ├── db/                      # Database layer
│   │   ├── __init__.py
│   │   └── storage.py           # In-memory storage (dictionaries)
│   │
│   ├── models/                  # Database/Domain models
│   │   └── __init__.py          # User, Task, Project models
│   │
│   ├── schemas/                 # Pydantic validation models
│   │   ├── __init__.py
│   │   ├── user.py             # User request/response schemas
│   │   ├── task.py             # Task schemas
│   │   ├── project.py          # Project schemas
│   │   └── query.py            # Query parameter schemas
│   │
│   ├── routers/                 # API route handlers
│   │   ├── __init__.py
│   │   ├── user.py             # /users endpoints (register, login, profile, update)
│   │   ├── task.py             # /tasks endpoints (CRUD, filtering, pagination)
│   │   └── project.py          # /projects endpoints (CRUD)
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication logic (login, refresh token)
│   │   ├── user_service.py     # User business logic (register, profile)
│   │   ├── task_service.py     # Task business logic (CRUD, filtering)
│   │   └── project_service.py  # Project business logic (CRUD, task assignment)
│   │
│   └── dependencies/            # FastAPI dependency injection
│       ├── __init__.py
│       ├── user.py             # get_current_user, get_admin_user
│       └── task.py             # get_task_or_404
│
├── tests/                       # Test suite (129 tests total)
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures and configuration
│   │
│   ├── unit/                   # Unit tests (47 tests - Business logic isolation)
│   │   ├── __init__.py
│   │   ├── test_auth_service.py         # Login & refresh token logic (9 tests)
│   │   ├── test_user_service.py        # User CRUD operations (13 tests)
│   │   ├── test_task_service.py        # Task business logic (13 tests)
│   │   └── test_project_service.py     # Project logic (12 tests)
│   │
│   ├── test_auth.py            # Integration: User authentication (26 tests)
│   ├── test_tasks.py           # Integration: Task CRUD via HTTP (36 tests)
│   └── test_projects.py        # Integration: Project management (20 tests)
│
├── requirements.txt             # Python dependencies
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules
├── pyproject.toml              # Project metadata
├── pyrightconfig.json          # Pyright type checking config
├── run.sh                      # Start script for macOS/Linux
├── run.bat                     # Start script for Windows
└── README.md                   # This file
```

## API Endpoints

All authenticated endpoints require a JWT access token:
```
Authorization: Bearer <your-access-token>
```

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /users/register | Register new user | No |
| POST | /users/login | Login & get token | No |
| GET | /users/me | Get current profile | Yes |
| PUT | /users/me | Update profile | Yes |
| POST | /tasks | Create task | Yes |
| GET | /tasks | List my tasks | Yes |
| GET | /tasks/{id} | Get task details | Yes |
| PUT | /tasks/{id} | Update task | Yes |
| DELETE | /tasks/{id} | Delete task | Yes |
| POST | /projects | Create project | Yes |
| GET | /projects | List my projects | Yes |

**Query Parameters for Task List:**
- `?status=todo` - Filter by status (todo, in_progress, done)
- `?search=keyword` - Search by task title
- `?page=1` - Pagination (default: page 1)
- `?limit=10` - Items per page (default: 10)

### Example Requests

```bash
# Register User
POST /users/register
Body: {"email": "user@example.com", "password": "SecurePass123!"}

# Login
POST /users/login
Body: username=user@example.com&password=SecurePass123!

# Create Task
POST /tasks
Headers: Authorization: Bearer <access-token>
Body: {"title": "Learn FastAPI", "description": "Complete the tutorial", "status": "todo"}

# List Tasks
GET /tasks?status=todo&search=FastAPI&page=1&limit=10
Headers: Authorization: Bearer <access-token>
```

## Running Tests

### Test Structure

This project uses **two types of tests**:

1. **Unit Tests (47 tests)** - Test business logic in isolation with mocked dependencies
   - Location: `tests/unit/`
   - Files: `test_auth_service.py`, `test_user_service.py`, `test_task_service.py`, `test_project_service.py`
   - Use: pytest with unittest.mock (patch, MagicMock)
   - Focus: Login/Refresh token logic, User/Task/Project CRUD operations

2. **Integration Tests (82 tests)** - Test HTTP endpoints with real database state
   - Location: `tests/test_auth.py`, `tests/test_tasks.py`, `tests/test_projects.py`
   - Use: FastAPI TestClient (httpx)
   - Focus: HTTP status codes, response formats, end-to-end workflows

### Running Tests

```bash
# Run all tests (129 total)
pytest tests/ -v

# Run only unit tests (47 tests)
pytest tests/unit/ -v

# Run only integration tests (82 tests)
pytest tests/ --ignore=tests/unit -v

# Run specific test file
pytest tests/unit/test_auth_service.py -v

# Run specific test class
pytest tests/unit/test_auth_service.py::TestLoginService -v

# Run specific test
pytest tests/unit/test_auth_service.py::TestLoginService::test_login_success -v

# Quick check (quiet mode)
pytest tests/unit/ -q

# Generate coverage report
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

| Component | Unit Tests | Integration Tests | Total |
|-----------|-----------|------------------|-------|
| **Authentication** | 9 (Login, Refresh token) | 26 (Register, Login, Profile) | 35 |
| **User Service** | 13 (CRUD, profiles) | — | 13 |
| **Task Service** | 13 (CRUD, filtering) | 36 (API endpoints) | 49 |
| **Project Service** | 12 (CRUD, assignment) | 20 (API endpoints) | 32 |
| **TOTAL** | **47** | **82** | **129** |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | dev-key | JWT signing key (change in production) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiry time in minutes |
| `ALGORITHM` | HS256 | JWT algorithm |
| `DEBUG` | False | Debug mode |

## Troubleshooting

### "Not authenticated" Error

**Problem**: Endpoints return 401 Unauthorized

**Solution**:
1. Register user: `POST /users/register`
2. Login: `POST /users/login` (receive access_token)
3. Use token in Authorization header: `Authorization: Bearer <token>`
4. Test endpoint again

### Token Expired

**Problem**: JWT token expired (usually after 30 minutes)

**Solution**: Login again to get a new access token

### Task Not Found (404)

**Problem**: Trying to access another user's task

**Solution**: Users can only access tasks they created. Verify you're accessing your own resources.

### Port Already in Use

**Problem**: Cannot run server on port 8000 (already in use)

**Solution**:
```bash
# Run on different port
uvicorn app.main:app --port 8001 --reload
```

## License

This is a learning project for educational purposes.
