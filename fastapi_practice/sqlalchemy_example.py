"""
SQLAlchemy Setup & CRUD Operations Example
==========================================

Complete example of:
1. SQLAlchemy configuration
2. Database models
3. CRUD operations (Create, Read, Update, Delete)
"""

# ==================== 1. IMPORTS ====================
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# ==================== 2. DATABASE SETUP ====================

# Option 1: SQLite (easy, no setup required)
DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "sqlite:///test.db"  # test.db file will be created in the code directory

# Option 2: PostgreSQL (production)
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Option 3: MySQL
# DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"

# ==================== 3. ENGINE & SESSION ====================

# Engine: Database connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# SessionLocal: Create session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: Use to define models
Base = declarative_base()

# ==================== 4. MODELS (Database Schema) ====================


class User(Base):
    """User model - Represents the users table in the database"""

    __tablename__ = "users"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: 1 user has many tasks
    tasks = relationship("Task", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Task(Base):
    """Task model - Represents the tasks table in the database"""

    __tablename__ = "tasks"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    status = Column(String, default="todo")  # todo, in_progress, done
    user_id = Column(Integer, ForeignKey("users.id"))  # Foreign key
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: Each task belongs to 1 user
    owner = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, user_id={self.user_id})>"


# ==================== 5. CREATE TABLES ====================


def create_tables():
    """Create all tables (run once when setting up the database)"""
    Base.metadata.create_all(bind=engine)
    print("Tables created!")


# ==================== 6. CRUD OPERATIONS ====================

# ========== CREATE (Add data) ==========


def create_user(db, email: str, username: str, hashed_password: str):
    """
    CREATE: Add a new user to the database

    Usage:
    db = SessionLocal()
    user = create_user(db, "user@example.com", "testuser", "hashed123")
    print(f"Created: {user}")
    """
    # 1. Create User object
    user = User(email=email, username=username, hashed_password=hashed_password)

    # 2. Add to session
    db.add(user)

    # 3. Commit (save to database)
    db.commit()

    # 4. Refresh (fetch data from DB, needed to get auto-generated fields like id)
    db.refresh(user)

    return user


def create_task(db, title: str, description: str, user_id: int):
    """
    CREATE: Add a new task to the database

    Usage:
    task = create_task(db, "Learn FastAPI", "Study FastAPI basics", user_id=1)
    """
    task = Task(title=title, description=description, user_id=user_id, status="todo")
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# ========== READ (Get data) ==========


def get_user_by_id(db, user_id: int):
    """
    READ: Get user by ID

    Usage:
    user = get_user_by_id(db, 1)
    """
    user = db.query(User).filter(User.id == user_id).first()
    return user
    # .first() → Get first record
    # .all() → Get all records


def get_user_by_email(db, email: str):
    """READ: Get user by email"""
    user = db.query(User).filter(User.email == email).first()
    return user


def get_all_users(db):
    """READ: Get all users"""
    users = db.query(User).all()
    return users


def get_user_tasks(db, user_id: int):
    """READ: Get all tasks for a user"""
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks


def get_task_by_id(db, task_id: int):
    """READ: Get task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    return task


def get_all_tasks(db):
    """READ: Get all tasks"""
    tasks = db.query(Task).all()
    return tasks


def search_tasks(db, search_term: str):
    """READ: Search tasks by keyword"""
    tasks = db.query(Task).filter(Task.title.ilike(f"%{search_term}%")).all()
    # .ilike() → Case-insensitive search
    return tasks


# ========== UPDATE (Update data) ==========


def update_user(db, user_id: int, email: str = None, username: str = None):
    """
    UPDATE: Update user information

    Usage:
    updated_user = update_user(db, 1, email="newemail@example.com")
    """
    # 1. Get user from database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    # 2. Update fields
    if email:
        user.email = email
    if username:
        user.username = username

    # 3. Commit
    db.commit()
    db.refresh(user)

    return user


def update_task(db, task_id: int, title: str = None, status: str = None):
    """
    UPDATE: Update task

    Usage:
    updated_task = update_task(db, 1, title="New Title", status="in_progress")
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return None

    if title:
        task.title = title
    if status:
        task.status = status

    # updated_at is automatically updated by onupdate=datetime.utcnow
    db.commit()
    db.refresh(task)

    return task


# ========== DELETE (Delete data) ==========


def delete_user(db, user_id: int):
    """
    DELETE: Delete user

    Usage:
    delete_user(db, 1)
    """
    # 1. Get user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return False

    # 2. Delete
    db.delete(user)

    # 3. Commit
    db.commit()

    return True


def delete_task(db, task_id: int):
    """DELETE: Delete task"""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return False

    db.delete(task)
    db.commit()

    return True


# ==================== 8. EXAMPLE USAGE ====================


def example_full_workflow():
    """Complete example: Create → Read → Update → Delete"""

    # Setup
    create_tables()  # Create tables
    db = SessionLocal()

    try:
        print("\n========== CREATE ==========")
        # 1. Create user
        user = create_user(db, "john@example.com", "john_doe", "hashed_password_123")
        print(f"Created: {user}")

        # 2. Create tasks
        task1 = create_task(db, "Learn SQLAlchemy", "Study ORM basics", user.id)
        task2 = create_task(db, "Build API", "Create FastAPI endpoints", user.id)
        print(f"Created: {task1}")
        print(f"Created: {task2}")

        print("\n========== READ ==========")
        # 3. Get user
        fetched_user = get_user_by_id(db, user.id)
        print(f"Found: {fetched_user}")

        # 4. Get user's tasks
        user_tasks = get_user_tasks(db, user.id)
        print(f"User {user.username} has {len(user_tasks)} tasks:")
        for task in user_tasks:
            print(f"   - {task.title} ({task.status})")

        # 5. Search
        search_results = search_tasks(db, "Learn")
        print(f"Search results for 'Learn': {len(search_results)} tasks")

        print("\n========== UPDATE ==========")
        # 6. Update user
        updated_user = update_user(db, user.id, email="john.new@example.com")
        print(f"Updated: {updated_user}")

        # 7. Update task
        updated_task = update_task(db, task1.id, status="in_progress")
        print(f"Updated: {updated_task}")

        print("\n========== DELETE ==========")
        # 8. Delete task
        delete_task(db, task2.id)
        print(f"Deleted task {task2.id}")

        # 9. Delete user (will delete related tasks if CASCADE is set)
        delete_user(db, user.id)
        print(f"Deleted user {user.id}")

        # 10. Verify
        remaining_users = get_all_users(db)
        print(f"\nRemaining users: {len(remaining_users)}")

    finally:
        db.close()


# ==================== 9. KEY CONCEPTS ====================

"""
Query:
- db.query(User).filter(...).first()  → Get 1 record
- db.query(User).filter(...).all()    → Get all records
- db.query(User).filter(...).count()  → Count records

Filter conditions:
- User.id == 1
- User.email == "test@example.com"
- User.is_active == True
- User.title.ilike("%Learn%")  → Like search
- Task.user_id.in_([1, 2, 3]) → IN clause

Relationships:
- user.tasks → Get all tasks of user (through relationship)
"""

# ==================== 10. ADVANCED EXAMPLES ====================


def advanced_queries(db):
    """Advanced queries"""

    # Filter with multiple conditions
    user = (
        db.query(User)
        .filter((User.email == "john@example.com") & (User.is_active == True))
        .first()
    )

    # Order by
    users = db.query(User).order_by(User.created_at.desc()).all()

    # Limit & Offset (pagination)
    page = 1
    limit = 10
    users = db.query(User).limit(limit).offset((page - 1) * limit).all()

    # Count
    total_users = db.query(User).count()

    # With relationship (eager loading)
    user_with_tasks = db.query(User).filter(User.id == 1).first()
    print(user_with_tasks.tasks)  # Access relationship


if __name__ == "__main__":
    # Run example
    example_full_workflow()

    # Output:
    # Tables created!
    # ========== CREATE ==========
    # Created: <User(id=1, email=john@example.com, username=john_doe)>
    # Created: <Task(id=1, title=Learn SQLAlchemy, user_id=1)>
    # ...
