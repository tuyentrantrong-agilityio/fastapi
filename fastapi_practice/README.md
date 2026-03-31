# FastAPI Task Management Application

A comprehensive FastAPI learning project demonstrating user authentication, task CRUD operations, project management, and role-based access control. Features JWT-based authentication, Argon2id password hashing, task ownership enforcement, and 134 comprehensive tests (52 unit tests + 82 integration tests).

## Overview

This project builds a production-like task management API with:
- User authentication and authorization with JWT tokens and refresh token rotation
- Secure password hashing using Argon2id (OWASP recommended)
- Full CRUD operations for tasks with filtering, search, and pagination
- Role-based access control (user vs admin)
- Task ownership enforcement (users can only access their own tasks)
- Project management with task assignments
- **134 comprehensive tests** (52 unit tests + 82 integration tests)
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

#### 1. Clone repo
```bash
git clone git@gitlab.asoft-python.com:tuyen.trantrong/python.git
```

#### 2. Navigate to directory
```bash
cd python
git checkout feat/database-integration
cd fastapi_practice
```

#### 3. Create virtual environment
```bash
python -m venv .venv
```

#### 4. Activate venv

**PowerShell (Windows):**
```bash
.\.venv\Scripts\Activate.ps1
```

**cmd (Windows):**
```bash
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

#### 5. Install dependencies
```bash
pip install -e ".[dev]"
```

#### 6. Copy file config
```bash
cp .env.example .env
```

#### 7. Run uvicorn
```bash
uvicorn app.main:app --reload
```

#### 4. Access Application

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
│   │   ├── base.py              # SQLModel base configuration
│   │   ├── session.py           # AsyncSession factory for database connections
│   │   └── init_db.py           # Database initialization functions
│   │
│   ├── models/                  # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── task.py              # Task model
│   │   ├── project.py           # Project model
│   │   └── refresh_token.py     # RefreshToken model for token rotation
│   │
│   ├── schemas/                 # Pydantic validation models (request/response)
│   │   ├── __init__.py
│   │   ├── user.py             # User request/response schemas
│   │   ├── task.py             # Task schemas
│   │   ├── project.py          # Project schemas
│   │   └── query.py            # Query parameter schemas
│   │
│   ├── routers/                 # API route handlers (HTTP endpoints)
│   │   ├── __init__.py
│   │   ├── user.py             # /users endpoints (register, login, profile, update)
│   │   ├── task.py             # /tasks endpoints (CRUD, filtering, pagination)
│   │   └── project.py          # /projects endpoints (CRUD)
│   │
│   ├── services/                # Business logic layer (SERVICE LAYER)
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication logic (login, refresh token)
│   │   ├── user_service.py     # User CRUD business logic
│   │   ├── task_service.py     # Task CRUD & filtering business logic
│   │   └── project_service.py  # Project business logic & task assignment
│   │
│   └── dependencies/            # FastAPI dependency injection
│       ├── __init__.py
│       ├── user.py             # get_current_user, get_admin_user dependencies
│       └── task.py             # get_task_or_404 dependency
│
├── alembic/                     # Database migrations (Alembic)
│   ├── env.py                   # Alembic runtime configuration
│   ├── script.py.mako           # Alembic migration template
│   ├── versions/                # Migration scripts (auto-generated)
│   │   └── [migration files]   # e.g., *_create_user_table.py
│   └── README                   # Alembic documentation
│
├── tests/                       # Test suite (134 tests total)
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures and database setup
│   │
│   ├── unit/                   # Unit tests (52 tests - Business logic with mocks)
│   │   ├── __init__.py
│   │   ├── test_auth_service.py         # Login & refresh token logic
│   │   ├── test_user_service.py        # User CRUD operations
│   │   ├── test_task_service.py        # Task business logic & filtering
│   │   ├── test_project_service.py     # Project business logic
│   │   └── test_security.py            # JWT token generation, validation & hashing
│   │
│   ├── test_auth.py            # Integration: User authentication (26 tests)
│   ├── test_tasks.py           # Integration: Task CRUD via HTTP (38 tests)
│   └── test_projects.py        # Integration: Project management (18 tests)
│
├── pyproject.toml              # Project metadata, dependencies & pytest config
├── pyrightconfig.json          # Pyright type checking config
├── pyproject.toml              # Project metadata & pytest config
├── pyrightconfig.json          # Pyright type checking config
├── .env.example                # Example environment variables
├── alembic.ini                 # Alembic configuration
├── .gitignore                  # Git ignore rules
├── run.sh                      # Start script for macOS/Linux
├── run.bat                     # Start script for Windows
└── README.md                   # This file
```

## Layered Architecture

This project follows a **three-tier layered architecture** for clean code separation:

```
┌─────────────────────────────────────────────────┐
│   HTTP Request  (Browser, Postman, TestClient)  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Router Layer (API Endpoints)                   │
│  ├── /users/register, /users/login              │
│  ├── /tasks (CRUD + filtering + pagination)     │
│  └── /projects (CRUD + task assignment)         │
│  Responsibility: Validate input, handle HTTP    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Service Layer (Business Logic)                 │
│  ├── auth_service: Login, token refresh         │
│  ├── user_service: User CRUD operations         │
│  ├── task_service: Task CRUD, filtering         │
│  └── project_service: Project management        │
│  Responsibility: Core business logic, rules     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Database Layer (SQLite + Alembic)              │
│  ├── Models: User, Task, Project, RefreshToken  │
│  ├── Session: AsyncSession for async queries    │
│  └── Migrations: Version control via Alembic    │
│  Responsibility: Data persistence & schema mgmt │
└─────────────────────────────────────────────────┘
```

**Data Flow Example: Creating a Task**

1. **HTTP Request** → `POST /tasks {"title": "Learn FastAPI"}`
2. **Router** → Validates input with TaskCreate schema, calls service layer
3. **Service** → `create_task_service()` → Checks user ownership, creates Task model
4. **Database** → Inserts Task row, returns created object
5. **Response** → Returns TaskResponse (status 201)

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

## Database Setup & Migrations

This project uses **SQLite** for development and **Alembic** for database schema version control.

### Initial Database Setup

Before running the application for the first time, you need to apply migrations:

```bash
# Apply all migrations to create database schema
alembic upgrade head
```

This command:
- Creates `app.db` (SQLite database file)
- Runs all pending migration scripts in `alembic/versions/`
- Sets `alembic_version` table with latest schema version

### Running the Application with Fresh Database

```bash
# 1. Apply migrations (one-time setup)
alembic upgrade head

# 2. Run the server
uvicorn app.main:app --reload

# Access at http://localhost:8000/docs
```

### Migration Workflow

```bash
# Check current migration status
alembic current

# Create new migration after modifying models
alembic revision --autogenerate -m "description of changes"

# Upgrade to latest version
alembic upgrade head

# Downgrade to previous version
alembic downgrade -1

# View migration history
alembic history
```

### Alembic Directory Structure

```
alembic/
├── env.py                          # Runtime config & connection setup
├── script.py.mako                  # Template for auto-generated migrations
├── alembic.ini                     # Alembic settings (also in root)
├── versions/                       # Migration scripts folder
│   ├── [revision_id]_[description].py
│   └── ...
└── README                          # Alembic documentation
```

## Running Tests

### Test Structure

This project uses **two types of tests**:

1. **Unit Tests (40 tests)** - Test business logic in isolation with mocked dependencies
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
# Run all tests (122 total)
pytest tests/ -v

# Run only unit tests (40 tests)
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
| **Authentication** | 8 (Login, Refresh token) | 26 (Register, Login, Profile) | 34 |
| **User Service** | 7 (CRUD, profiles) | — | 7 |
| **Task Service** | 13 (CRUD, filtering) | 38 (API endpoints) | 51 |
| **Project Service** | 12 (CRUD, assignment) | 18 (API endpoints) | 30 |
| **TOTAL** | **40** | **82** | **122** |

## Learning Curriculum & Progress

This project demonstrates key FastAPI concepts in a structured progression:

### PART 1 FASTAPI BASICS
- [x] FastAPI application setup and routing
- [x] Request/response models with Pydantic
- [x] Path parameters and query parameters
- [x] Request body validation

### PART 2 INTERMEDIATE FASTAPI  
- [x] Dependency injection (`Depends()`)
- [x] JWT authentication with Bearer tokens
- [x] Role-based access control (RBAC)
- [x] Custom exception handlers
- [x] CORS configuration

### PART 3 DATABASE INTEGRATION
- [x] SQLModel ORM with SQLite
- [x] Async database sessions (AsyncSession)
- [x] Alembic migrations for schema versioning
- [x] Database model relationships (Foreign Keys)
- [x] Query filtering and pagination

###  AUTHENTICATION & AUTHORIZATION
- [x] User registration with validation
- [x] Secure password hashing (Argon2id)
- [x] JWT token generation and validation
- [x] Refresh token rotation for security
- [x] User role-based permissions

###  ADVANCED FEATURES
- [x] Task filtering, searching, and sorting
- [x] Task pagination with metadata
- [x] User data isolation (task ownership)
- [x] Project management and task assignments
- [x] Complex nested relationships

###  TESTING
- [x] Unit tests with mocked dependencies (40 tests)
- [x] Integration tests with real HTTP endpoints (82 tests)
- [x] Test fixtures and database setup
- [x] Async test support with pytest-asyncio
- [x] API endpoint validation

## Debugging Tests with VSCode

### Setup Python Debugger

1. **Install VSCode Python Extension:**
   - Open VSCode → Extensions → Search "Python" → Install "Python" by Microsoft

2. **Configure debugger in `.vscode/launch.json`:**
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Pytest: Unit Tests",
         "type": "python",
         "request": "launch",
         "module": "pytest",
         "args": ["tests/unit/", "-v", "-s"],
         "console": "integratedTerminal",
         "justMyCode": true
       },
       {
         "name": "Pytest: Integration Tests",
         "type": "python",
         "request": "launch",
         "module": "pytest",
         "args": ["tests/test_auth.py", "-v", "-s"],
         "console": "integratedTerminal",
         "justMyCode": true
       }
     ]
   }
   ```

3. **Debug a specific test:**
   - Open test file (`tests/unit/test_auth_service.py`)
   - Click line number to set breakpoint
   - Press `F5` or Run → Start Debugging
   - VSCode will pause at breakpoint, allowing you to inspect variables

4. **Debug shortcuts:**
   - `F5` - Start/Continue
   - `F10` - Step Over
   - `F11` - Step Into
   - `Shift+F11` - Step Out
   - `Ctrl+K Ctrl+I` - Show hovering value

### Debug via Terminal

```bash
# Run pytest with verbose output and print statements
pytest tests/unit/test_auth_service.py -v -s

# Run specific test with debugging
pytest tests/unit/test_auth_service.py::TestLoginService::test_success -v -s --tb=short

# Drop into pdb debugger on failure
pytest tests/unit/ -v --pdb
```

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
