# Practice 1 - FastAPI Task Management Application

A comprehensive FastAPI learning project demonstrating user authentication, task CRUD operations, and role-based access control with extensive test coverage.

## 📋 Overview

**Practice 1** is a production-like task management API built with FastAPI, featuring:
- **User Authentication** - Registration, login with JWT tokens
- **Password Security** - Argon2id hashing (no length limitations)
- **Task Management** - Full CRUD operations with filtering, search, and pagination
- **Authorization** - Role-based access control (user vs admin)
- **Task Ownership** - Users can only access/modify their own tasks
- **Comprehensive Testing** - 49 unit tests covering all major functionality
- **Professional Structure** - Modular architecture with clear separation of concerns

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | 0.128.0 |
| **ASGI Server** | Uvicorn | Latest |
| **Data Validation** | Pydantic | 2.12.5 |
| **Security/Hashing** | Argon2-cffi | Latest |
| **JWT Tokens** | python-jose | Latest |
| **Testing** | Pytest | 9.0.2 |
| **Async Testing** | pytest-asyncio | 1.3.0 |
| **HTTP Client** | httpx | 0.28.1 |
| **Python** | 3.11+ | - |

## ⚡ Quick Start

### **1. Clone Repository**
```bash
git clone <repository-url>
cd python-practice
```

### **2. Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run Application**
```bash
# Using main.py
python main.py

# Or using uvicorn directly
uvicorn app.main:app --reload

# Or using run script (macOS/Linux)
./run.sh
```

### **5. Access API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **6. Run Tests**
```bash
pytest tests/
# With verbose output
pytest tests/ -v
```

## 📁 Project Structure

```
python-practice/
├── app/                         # Main application package
│   ├── __init__.py             # Package initialization
│   ├── main.py                 # FastAPI app instance & setup
│   │
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py           # Settings & configuration
│   │   ├── hashing.py          # Password hashing (argon2id)
│   │   ├── security.py         # JWT token management
│   │   ├── exceptions.py       # Custom exception classes
│   │   └── handlers.py         # Global exception handlers
│   │
│   ├── db/                     # Database layer
│   │   ├── __init__.py
│   │   ├── storage.py          # In-memory storage (dicts)
│   │   └── migrations/         # Migration scripts (if needed)
│   │
│   ├── models/                 # Database/Domain models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── task.py            # Task model
│   │   └── project.py         # Project model
│   │
│   ├── schemas/                # Pydantic models (validation)
│   │   ├── __init__.py
│   │   ├── user.py            # User request/response schemas
│   │   ├── task.py            # Task schemas
│   │   ├── project.py         # Project schemas
│   │   └── query.py           # Query parameter schemas
│   │
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── user.py            # /users endpoints (register, login, profile)
│   │   ├── task.py            # /tasks endpoints (CRUD + filtering)
│   │   └── project.py         # /projects endpoints (CRUD)
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py    # User business logic
│   │   └── task_service.py    # Task business logic
│   │
│   └── dependencies/           # FastAPI dependency injection
│       ├── __init__.py
│       ├── user.py            # get_current_user, get_admin_user
│       └── task.py            # get_task_or_404
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_main.py           # Main endpoint tests
│   ├── test_users.py          # User endpoint tests
│   ├── test_tasks.py          # Task endpoint tests
│   └── test_projects.py       # Project endpoint tests
│
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version
├── pyproject.toml              # Project configuration
├── pyrightconfig.json          # Pyright configuration
├── run.sh                      # Start script (Unix/Mac)
├── run.bat                     # Start script (Windows)
└── README.md                   # This file
```

## 🚀 Setup Instructions for Developers
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install fastapi uvicorn pydantic pydantic-settings passlib argon2-cffi python-jose cryptography pytest pytest-asyncio httpx
```

Or from requirements (if exists):
```bash
pip install -r requirements.txt
```

5. **Create .env file**
```env
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
DEBUG=True
```

## 🔧 Running the Application

### Development Server

```bash
python -m uvicorn main:app --reload
```

**Output:**
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

**Access:**
- 📚 **API Docs (Swagger UI)**: http://localhost:8000/docs
- 📖 **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- 🏠 **Home**: http://localhost:8000/

### Production Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

**Output:**
```
tests/test_auth.py ..................      [ 36%]
tests/test_auth_errors.py ..............  [ 65%]
tests/test_tasks.py .................     [100%]

===================== 49 passed, 13 warnings in 2.34s =====================
```

### Run Specific Test File

```bash
# Authentication tests only
pytest tests/test_auth.py -v

# Task CRUD tests only
pytest tests/test_tasks.py -v

# Error handling tests only
pytest tests/test_auth_errors.py -v
```

### Run Specific Test Class or Function

```bash
# Single test class
pytest tests/test_auth.py::TestRegister -v

# Single test function
pytest tests/test_auth.py::TestRegister::test_register_success -v
```

### Run with Coverage

```bash
pytest tests/ --cov=core --cov=routers --cov=schemas --cov=dependencies
```

### Run with Detailed Output

```bash
pytest tests/ -vv --tb=long
```

## 📝 Test Coverage

| Module | Test File | Test Count | Coverage |
|--------|-----------|-----------|----------|
| **Authentication** | test_auth.py | 19 | Register, Login, Profile, Protected endpoints |
| **Task CRUD** | test_tasks.py | 18 | Create, Read, Update, Delete, Pagination |
| **Authorization** | test_auth_errors.py | 12 | Ownership, Permissions, Error handling |
| **Total** | **49 tests** | **All major features** | ✅ |

## 🔐 API Endpoints

### User Management

```bash
# Register new user
POST /users/register
Body: {"email": "user@example.com", "password": "pass1234"}
Response: 201 Created

# Login (get JWT token)
POST /users/login
Body: username=user@example.com&password=pass1234
Response: {"access_token": "...", "token_type": "bearer"}

# Get current user profile
GET /users/me
Headers: Authorization: Bearer <token>
Response: {"id": 1, "email": "user@example.com", "role": "user"}

# Update user profile
PUT /users/me
Headers: Authorization: Bearer <token>
Body: {"email": "newemail@example.com", "password": "newpass1234"}
Response: {"id": 1, "email": "newemail@example.com", "role": "user"}
```

### Task Management

```bash
# Create task
POST /tasks
Headers: Authorization: Bearer <token>
Body: {"title": "Learn FastAPI", "description": "Complete the course", "status": "todo"}
Response: 201 Created with task data

# Get all tasks (with filtering & pagination)
GET /tasks?status=todo&search=keyword&page=1&limit=10
Headers: Authorization: Bearer <token>
Response: {"data": [...], "pagination": {...}}

# Get single task
GET /tasks/{id}
Headers: Authorization: Bearer <token>
Response: Task details

# Update task
PUT /tasks/{id}
Headers: Authorization: Bearer <token>
Body: {"title": "Updated Title", "status": "done"}
Response: Updated task

# Delete task
DELETE /tasks/{id}
Headers: Authorization: Bearer <token>
Response: 200 OK
```

### Project Management

```bash
# Create project
POST /projects
Headers: Authorization: Bearer <token>
Body: {"name": "My Project", "description": "Project description"}
Response: 201 Created

# Get projects
GET /projects
Headers: Authorization: Bearer <token>
Response: List of user's projects
```

## 🔑 Key Features

### Authentication Flow

```
User Registration → Password Hashing (Argon2id) → DB Storage
                   ↓
User Login → Verify Password → Generate JWT Token
            ↓
Protected Endpoints ← Token Validation ← Get Current User
```

### Password Security

- **Algorithm**: Argon2id (OWASP recommended)
- **Length**: No limitations (unlike bcrypt's 72-byte limit)
- **Hashing**: One-way irreversible hashing
- **Verification**: Constant-time comparison

### Authorization

- **Role-Based Access Control (RBAC)**
  - `user` - Standard user role
  - `admin` - Administrative privileges
  
- **Task Ownership**
  - Each task has `user_id`
  - Users can only access their own tasks
  - Enforced at dependency level

### Error Handling

All errors return standardized JSON format:

```json
{
  "error": {
    "message": "User not found",
    "detail": "User with id 999 not found",
    "status_code": 404
  }
}
```

Status Codes:
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

## 📚 API Documentation

### Quick Start
See [GUIDE.md](GUIDE.md) for a quick reference guide.

### Complete Documentation
See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for detailed documentation.

## 🧑‍💻 Development Workflow

### 1. Start Development Server

```bash
python -m uvicorn main:app --reload
```

### 2. Access Swagger UI

Open http://localhost:8000/docs

### 3. Authorize (for testing protected endpoints)

- Click **"Authorize"** button
- Enter credentials:
  - **username**: user@example.com
  - **password**: pass1234
- Click **"Authorize"**

### 4. Test Endpoints

Try out any endpoint in Swagger UI

### 5. Run Tests

```bash
pytest tests/ -v
```

## 🛡️ Security Considerations

| Aspect | Implementation |
|--------|----------------|
| **Password Hashing** | Argon2id (OWASP recommended) |
| **Tokens** | JWT with HS256 signature |
| **Token Expiry** | 30 minutes (configurable) |
| **Input Validation** | Pydantic with email verification |
| **SQL Injection** | N/A (in-memory storage) |
| **CORS** | Not enabled (for learning) |

## 🐛 Troubleshooting

### "Not authenticated" Error

**Problem**: Endpoints return 401 when testing without token

**Solution**: 
1. Register user: `POST /users/register`
2. Login: `POST /users/login` (get token)
3. Authorize in Swagger UI with token
4. Try endpoint again

### Password Too Long Error

**Problem**: Old bcrypt implementation with 72-byte limit

**Solution**: Already fixed! Using Argon2id now (unlimited length)

### Token Expired

**Problem**: JWT token expired (default 30 minutes)

**Solution**: Login again to get new token

### Task Not Found

**Problem**: User trying to access another user's task

**Solution**: Users can only access tasks they created

## 📦 Dependencies

Key dependencies and their purposes:

```python
# Web framework
fastapi==0.128.0           # Web framework
uvicorn                    # ASGI server

# Data validation
pydantic==2.12.5          # Request/response validation
pydantic-settings         # Settings management
email-validator           # Email validation

# Security
argon2-cffi               # Password hashing
python-jose               # JWT token handling
cryptography              # Cryptographic operations

# Testing
pytest==9.0.2            # Testing framework
pytest-asyncio==1.3.0    # Async test support
httpx==0.28.1            # Async HTTP client
```

## 📋 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | dev-key | JWT signing key (change in production) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiry time in minutes |
| `ALGORITHM` | HS256 | JWT algorithm |
| `DEBUG` | False | Debug mode (True for development) |

## 🎯 Learning Outcomes

After studying this project, you'll understand:

1. ✅ **FastAPI Fundamentals** - Routing, validation, responses
2. ✅ **Authentication** - JWT tokens, password hashing, OAuth2
3. ✅ **Authorization** - Role-based access, ownership verification
4. ✅ **Database Design** - User-owned resources, relationships
5. ✅ **Filtering & Search** - Multi-parameter filtering, pagination
6. ✅ **Error Handling** - Custom exceptions, standardized responses
7. ✅ **Testing** - Unit tests, fixtures, mocking
8. ✅ **Security** - Password hashing, token validation
9. ✅ **Modular Architecture** - Separation of concerns
10. ✅ **Professional Practices** - Code organization, documentation

## 🚀 Next Steps

### Extend the Project

1. **Database**: Replace in-memory with PostgreSQL + SQLAlchemy
2. **Email**: Add email verification and password reset
3. **Caching**: Add Redis for token blacklist
4. **Logging**: Implement structured logging
5. **Deployment**: Docker, cloud platforms (Heroku, AWS)
6. **Frontend**: React/Vue UI for the API

### Deepen Your Learning

1. Learn async/await patterns
2. Understand JWT security implications
3. Study OWASP security guidelines
4. Explore database migrations
5. Learn about API versioning

## 📞 Support

For issues or questions:
1. Check [GUIDE.md](GUIDE.md) for quick answers
2. Review [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for details
3. Run tests to verify everything works
4. Check error responses for detailed messages

## 📄 License

This is a learning project. Feel free to use it for educational purposes.

---

**Last Updated**: March 10, 2026  
**Status**: ✅ Complete & Production-Ready  
**Test Coverage**: 49 tests passing
