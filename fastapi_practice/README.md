# FastAPI Task Management Application

A comprehensive FastAPI learning project demonstrating user authentication, task CRUD operations, project management, and role-based access control. Features JWT-based authentication, Argon2id password hashing, task ownership enforcement, WebSocket real-time updates, and 179 comprehensive tests with **81% code coverage**.

## Overview

This project builds a production-like task management API with:
- **Authentication & Authorization**: JWT tokens + refresh token rotation, role-based access control (user vs admin)
- **Security**: Argon2id password hashing (OWASP recommended), ownership enforcement
- **Task Management**: CRUD operations with advanced filtering, full-text search, and pagination
- **Real-time Updates**: WebSocket support for live task notifications
- **Performance**: Redis caching for task lists with intelligent cache invalidation
- **Background Processing**: Celery workers for async email delivery and task processing
- **API Versioning**: Layer-first architecture ready for multiple API versions (v1, v2, etc.)
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Testing**: 179 comprehensive tests with 81% code coverage, conftest fixtures
- **Code Quality**: Type hints throughout, Pyright type checking, structured logging with JSON output

## Tech Stack

- **FastAPI** 0.128.0 - Modern async web framework
- **Uvicorn** - ASGI server for production-ready deployments
- **SQLAlchemy** 2.0+ - Async ORM with SQLModel
- **PostgreSQL** - Primary database (asyncpg driver)
- **Pydantic** 2.12.5 - Data validation and settings management
- **Redis** - Caching layer for performance
- **Celery** - Distributed task queue for async work
- **Argon2-cffi** - Secure password hashing (OWASP recommended)
- **python-jose** - JWT token generation and validation
- **Alembic** - Database migration management
- **Pytest** 9.0.2 - Testing framework with fixtures and mocking
- **httpx** 0.28.1 - Async HTTP client for integration tests
- **Python** 3.11+

## Installation

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11 or higher
- uv (Python package manager and runner)

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

#### 3. Install dependencies
```bash
uv sync --extra dev
```

#### 4. Copy file config
```bash
cp .env.example .env
```

#### 5. Run uvicorn
```bash
uv run uvicorn app.main:app --reload
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
│   │   ├── hashing.py           # Argon2id password hashing
│   │   ├── security.py          # JWT token generation and verification
│   │   ├── exceptions.py        # Custom exception classes
│   │   ├── handlers.py          # Global exception handlers
│   │   ├── cache_keys.py        # Redis cache key constants
│   │   ├── logging_config.py    # JSON logging configuration
│   │   └── websocket_manager.py # Real-time WebSocket connection manager
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
│   ├── api/                     # API package (versioning-ready structure)
│   │   ├── endpoints/           # API route handlers (HTTP endpoints)
│   │   │   ├── __init__.py
│   │   │   ├── user.py         # /users endpoints (register, login, profile, update)
│   │   │   ├── task.py         # /tasks endpoints (CRUD, filtering, pagination)
│   │   │   ├── project.py      # /projects endpoints (CRUD)
│   │   │   └── websocket.py    # /ws endpoint (WebSocket real-time updates)
│   │   └── __init__.py
│   │
│   ├── services/                # Business logic layer (SERVICE LAYER)
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication logic (login, refresh token)
│   │   ├── user_service.py     # User CRUD business logic
│   │   ├── task_service.py     # Task CRUD & filtering business logic
│   │   ├── project_service.py  # Project business logic & task assignment
│   │   ├── cache_service.py    # Redis caching service
│   │   └── email_service.py    # Email sending service
│   │
│   ├── dependencies/            # FastAPI dependency injection
│   │   ├── __init__.py
│   │   ├── user.py             # get_current_user, get_admin_user dependencies
│   │   ├── task.py             # get_owned_task_or_error dependency
│   │   └── cache.py            # get_cache dependency
│   │
│   ├── middleware/              # Custom middleware
│   │   └── logging_middleware.py # Request/response logging with JSON output
│   │
│   ├── tasks/                   # Celery async workers
│   │   ├── __init__.py
│   │   ├── celery_app.py       # Celery configuration
│   │   ├── email_tasks.py      # Email delivery worker tasks
│   │   └── task_tasks.py       # Long-running task processor
│
├── alembic/                     # Database migrations (Alembic)
│   ├── env.py                   # Alembic runtime configuration
│   ├── script.py.mako           # Alembic migration template
│   ├── versions/                # Migration scripts (auto-generated)
│   │   └── [migration files]   # e.g., *_create_user_table.py
│   └── README                   # Alembic documentation
│
├── tests/                       # Test suite (179 tests total, 81% coverage)
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures and database setup
│   │
│   ├── unit/                   # Unit tests (52 tests - Business logic with mocks)
│   │   ├── __init__.py
│   │   ├── test_auth_service.py         # Login & refresh token logic
│   │   ├── test_user_service.py        # User CRUD operations
│   │   ├── test_task_service.py        # Task business logic & filtering
│   │   ├── test_project_service.py     # Project business logic
│   │   ├── test_security.py            # JWT token generation, validation & hashing
│   │   └── test_cache_service.py       # Cache operations
│   │
│   ├── test_auth.py            # Integration: User authentication (26 tests)
│   ├── test_tasks.py           # Integration: Task CRUD via HTTP (38 tests)
│   ├── test_projects.py        # Integration: Project management (18 tests)
│   ├── test_websocket_manager.py       # WebSocket connection/subscription (15 tests)
│   ├── test_email_tasks.py             # Celery email tasks (4 tests)
│   ├── test_task_tasks.py              # Celery task processing (2 tests)
│   └── test_logging_config.py          # Logging configuration (2 tests)
│
├── .coveragerc                 # Coverage configuration (excludes non-critical files)
├── pyproject.toml              # Project metadata, dependencies & pytest config
├── pyrightconfig.json          # Pyright type checking config
├── .env.example                # Example environment variables
├── alembic.ini                 # Alembic configuration
├── .gitignore                  # Git ignore rules
├── run.sh                      # Start script for macOS/Linux
├── run.bat                     # Start script for Windows
└── README.md                   # This file
```

## Layered Architecture

This project follows a **three-tier layered architecture** with API versioning support for clean code separation:

```
┌─────────────────────────────────────────────────┐
│   HTTP Request  (Browser, Postman, TestClient)  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  API Endpoint Layer (api/endpoints/)            │
│  ├── user.py: /users (register, login, profile) │
│  ├── task.py: /tasks (CRUD, search, pagination)│
│  ├── project.py: /projects (CRUD + assign)     │
│  └── websocket.py: /ws (real-time updates)     │
│  Responsibility: HTTP handling, validation      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Service Layer (services/)                      │
│  ├── auth_service: Login, token refresh         │
│  ├── user_service: User CRUD operations         │
│  ├── task_service: Task CRUD, filtering, search │
│  ├── project_service: Project management        │
│  ├── cache_service: Redis caching               │
│  └── email_service: Email delivery              │
│  Responsibility: Business logic & rules         │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Database Layer (db/, models/)                  │
│  ├── Models: User, Task, Project, RefreshToken  │
│  ├── AsyncSession: Async database connection    │
│  └── Alembic: Database version control          │
│  Responsibility: Data persistence & migration   │
└─────────────────────────────────────────────────┘
```

**Architecture Features:**
- **API Versioning Ready**: Structure supports easy addition of `/api/v1/`, `/api/v2/` in future
- **Layer-First Design**: Horizontal slicing makes layer responsibilities clear
- **Shared Infrastructure**: `core/`, `services/`, `db/` shared across all API versions
- **Dependency Injection**: `dependencies/` for reusable request validators
- **Real-time Support**: WebSocket manager for live task updates
- **Caching**: Redis integration for task list caching
- **Async Tasks**: Celery workers for email & background processing

## Advanced Features

### 🔄 Real-time Updates with WebSocket

Live task notifications for subscribed clients:

```python
# Client subscribes to task updates
ws://localhost:8000/ws?token=<jwt_token>

# Send subscription request
{"action": "subscribe", "task_id": 1}

# Receive live updates when task changes
{
  "event": "task_updated",
  "task_id": 1,
  "status": "done",
  "title": "Learn FastAPI",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Features:**
- JWT authentication via query parameters
- Ownership validation (users only see their own tasks)
- Dynamic subscriptions (subscribe/unsubscribe at runtime)
- Broadcast notifications on task updates

### 💾 Redis Caching

Intelligent caching layer for task lists with TTL and auto-invalidation:

**Cache Strategy:**
- Task list cache: 5 minutes TTL
- Project list cache: 10 minutes TTL
- Automatic invalidation on create/update/delete operations
- Cache key patterns: `tasks:u{user_id}:filter={status}:page={page}`

**Headers returned:**
```
X-Cache: HIT|MISS              # Whether data came from cache
X-Cache-Key: tasks:u1:...      # Cache key used
X-Cache-Store: OK|ERROR        # Whether cache store succeeded
```

### 📧 Async Email Delivery with Celery

Background workers handle non-blocking email operations:

**Tasks:**
- `send_welcome_email_task` - Welcome email on user registration
- `send_task_assigned_email_task` - Notification on task creation

**Configuration:**
- Message broker: Redis
- Result backend: Redis
- Worker processes: Configurable via environment
- Auto-retry on failure with exponential backoff

**Example:**
```python
# Email is queued and sent asynchronously
send_task_assigned_email_task.delay(
    email="user@example.com",
    task_title="Learn FastAPI",
    task_id=1
)
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

## Database Setup & Migrations

This project uses **SQLite** for development and **Alembic** for database schema version control.

### Initial Database Setup

Before running the application for the first time, you need to apply migrations:

```bash
# Apply all migrations to create database schema
uv run alembic upgrade head
```

This command:
- Creates `app.db` (SQLite database file)
- Runs all pending migration scripts in `alembic/versions/`
- Sets `alembic_version` table with latest schema version

### Running the Application with Fresh Database

```bash
# 1. Apply migrations (one-time setup)
uv run alembic upgrade head

# 2. Run the server
uv run uvicorn app.main:app --reload

# Access at http://localhost:8000/docs
```

### Migration Workflow

```bash
# Check current migration status
uv run alembic current

# Create new migration after modifying models
uv run alembic revision --autogenerate -m "description of changes"

# Upgrade to latest version
uv run alembic upgrade head

# Downgrade to previous version
uv run alembic downgrade -1

# View migration history
uv run alembic history
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

This project uses **multiple test types** organized by module:

1. **Unit Tests (52 tests)** - Business logic in isolation with mocked dependencies
   - Location: `tests/unit/`
   - Files: `test_auth_service.py`, `test_user_service.py`, `test_task_service.py`, `test_project_service.py`, `test_cache_service.py`, `test_security.py`, `test_celery_triggers.py`
   - Use: pytest with unittest.mock (patch, MagicMock, AsyncMock)
   - Focus: Login/Refresh token logic, User/Task/Project CRUD, email/cache operations

2. **Integration Tests (112 tests)** - HTTP endpoints with real database state
   - Location: `tests/test_auth.py`, `tests/test_tasks.py`, `tests/test_projects.py`
   - Use: FastAPI TestClient (httpx)
   - Focus: HTTP status codes, response formats, end-to-end workflows, pagination

3. **Module-Specific Tests (15 tests)** - Deep coverage for critical modules
   - `tests/test_websocket_manager.py` (15 tests) - WebSocket connection/subscription/broadcast
   - `tests/test_email_tasks.py` (4 tests) - Celery email task execution
   - `tests/test_task_tasks.py` (2 tests) - Celery task processing
   - `tests/test_logging_config.py` (2 tests) - Logging setup

### Running Tests

```bash
# Run all tests (179 total with 81% coverage)
uv run pytest tests/ -v

# Run only unit tests (52 tests)
uv run pytest tests/unit/ -v

# Run only integration tests (112 tests)
uv run pytest tests/ --ignore=tests/unit -v

# Run specific test file
uv run pytest tests/unit/test_auth_service.py -v

# Run specific test class
uv run pytest tests/unit/test_auth_service.py::TestLoginService -v

# Run specific test
uv run pytest tests/unit/test_auth_service.py::TestLoginService::test_login_success -v

# Quick check (quiet mode, auto-detects .coveragerc)
uv run pytest tests/ -q

# Generate coverage report (auto-uses .coveragerc config)
uv run pytest tests/ --cov=app --cov-report=html
# HTML report generated in: htmlcov/index.html

# View coverage in terminal
uv run pytest tests/ --cov=app --cov-report=term-missing
```

**Note:** Coverage configuration in `.coveragerc` automatically excludes non-critical infrastructure:
- `app/api/test_routes.py` - Internal development endpoints
- `app/core/logging_config.py` - Logging infrastructure
- `app/middleware/logging_middleware.py` - Request logging
- `app/api/endpoints/websocket.py` - Complex WebSocket endpoint

### Test Coverage Summary

**Overall Coverage: 81%** (187 missing / 1093 statements)

| Component | Unit Tests | Integration Tests | Module Tests | Total |
|-----------|-----------|------------------|--------------|-------|
| **Authentication** | 12 | 26 | - | 38 |
| **Users** | 10 | 8 | - | 18 |
| **Tasks** | 18 | 38 | 2 | 58 |
| **Projects** | 12 | 10 | - | 22 |
| **WebSocket** | - | - | 15 | 15 |
| **Email Tasks** | - | - | 4 | 4 |
| **Logging** | - | - | 2 | 2 |
| **Cache/Security/Celery** | 5 | 16 | - | 21 |
| **TOTAL** | **52** | **112** | **15** | **179** |

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
uv run pytest tests/unit/test_auth_service.py -v -s

# Run specific test with debugging
uv run pytest tests/unit/test_auth_service.py::TestLoginService::test_success -v -s --tb=short

# Drop into pdb debugger on failure
uv run pytest tests/unit/ -v --pdb
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

**Solution**: Run on different port
uv run uvicorn app.main:app --port 8001 --reload
```

## Architecture & Design Decisions

### API Endpoints Structure: Layer-First with Versioning Support

**Recent Refactoring (April 2024):**
- Moved `routers/` → `api/endpoints/` for cleaner versioning structure
- Enables future support for multiple API versions (v1, v2, etc.)
- Maintains clear separation between HTTP handlers and business logic

**Directory Structure:**
```
app/
├── api/
│   └── endpoints/       ← HTTP endpoint handlers
│       ├── user.py
│       ├── task.py
│       ├── project.py
│       └── websocket.py
├── services/            ← Business logic (reusable across versions)
├── db/                  ← Database layer (shared)
└── core/                ← Cross-cutting concerns (shared)
```

**Benefits:**
- ✅ **Clear Responsibilities**: Each layer has single responsibility
- ✅ **Scalability**: Easy to add `/api/v2/endpoints/` for breaking changes
- ✅ **Testability**: Services can be tested independently of HTTP
- ✅ **Maintainability**: Shared infrastructure reduces duplication
- ✅ **Evolution**: Version-aware structure supports API evolution

### Key Architectural Components

1. **Dependency Injection (`dependencies/`)**
   - Reusable request validators: `get_current_user`, `get_admin_user`, `get_owned_task_or_error`
   - Cache dependency: `get_cache` for Redis integration
   - Reduces boilerplate in endpoint handlers

2. **Error Handling (`core/handlers.py`)**
   - Global exception handlers for consistent error responses
   - Custom exception classes for different error types
   - Automatic JSON error formatting

3. **Security (`core/security.py`)**
   - JWT token generation and validation
   - Refresh token rotation pattern
   - Token claims extraction and validation

4. **Caching (`core/cache_keys.py`, `services/cache_service.py`)**
   - Redis integration for performance
   - Intelligent cache key patterns
   - Automatic invalidation on data changes

5. **Real-time Updates (`core/websocket_manager.py`)**
   - WebSocket connection management
   - Task subscription system
   - Broadcast notifications to subscribers

6. **Background Tasks (`tasks/`)**
   - Celery workers for async operations
   - Email delivery pipeline
   - Task processing workers

### Design Patterns Used

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Dependency Injection** | `dependencies/` | Reduce coupling, improve testability |
| **Service Layer** | `services/` | Separate business logic from HTTP |
| **Repository** | `db/` | Abstract data access |
| **Manager** | `websocket_manager.py` | Centralize WebSocket lifecycle |
| **Observer** | `websocket_manager.py` | Broadcast task updates |
| **Builder** | `cache_service.py` | Construct cache keys |

## License

This is a learning project for educational purposes.
