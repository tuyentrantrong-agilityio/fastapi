"""
SQLModel Setup & CRUD Operations Example
=========================================

Complete example of:
1. SQLModel configuration
2. Database models
3. CRUD operations (Create, Read, Update, Delete)
"""

# ==================== 1. IMPORTS ====================
from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func

# ==================== 2. DATABASE SETUP ====================

# Option 1: SQLite (easy, no setup required)
DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "sqlite:///test.db"  # test.db file will be created in the code directory

# Option 2: PostgreSQL (production)
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Option 3: MySQL
# DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"

# ==================== 3. ENGINE & SESSION ====================

# Engine: Database connection (SQLite needs check_same_thread=False)
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def get_session():
    """Get database session for each request"""
    with Session(engine) as session:
        yield session


# ==================== 4. MODELS (Database Schema) ====================


class User(SQLModel, table=True):
    """User model - Represents the users table in the database"""

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(index=True, unique=True)
    username: str = Field(unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship: 1 user has many tasks
    tasks: list["Task"] = Relationship(back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Task(SQLModel, table=True):
    """Task model - Represents the tasks table in the database"""

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    status: str = Field(default="todo")  # todo, in_progress, done
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship: Each task belongs to 1 user
    owner: Optional[User] = Relationship(back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, user_id={self.user_id})>"


# ==================== 5. CREATE TABLES ====================


def create_tables():
    """Create all tables (run once when setting up the database)"""
    SQLModel.metadata.create_all(engine)
    print("Tables created!")


# ==================== 6. CRUD OPERATIONS ====================

# ========== CREATE (Add data) ==========


def create_user(session, email: str, username: str, hashed_password: str):
    """
    CREATE: Add a new user to the database

    Usage:
    session = Session(engine)
    user = create_user(session, "user@example.com", "testuser", "hashed123")
    print(f"Created: {user}")
    """
    # 1. Create User object
    user = User(email=email, username=username, hashed_password=hashed_password)

    # 2. Add to session
    session.add(user)

    # 3. Commit (save to database)
    session.commit()

    # 4. Refresh (fetch data from DB, needed to get auto-generated fields like id)
    session.refresh(user)

    return user


def create_task(session, title: str, description: str, user_id: int):
    """
    CREATE: Add a new task to the database

    Usage:
    task = create_task(session, "Learn FastAPI", "Study FastAPI basics", user_id=1)
    """
    task = Task(title=title, description=description, user_id=user_id, status="todo")
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# ========== READ (Get data) ==========


def get_user_by_id(session, user_id: int):
    """
    READ: Get user by ID

    Usage:
    user = get_user_by_id(session, 1)
    """
    return session.get(User, user_id)


def get_user_by_email(session, email: str):
    """READ: Get user by email"""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_all_users(session):
    """READ: Get all users"""
    statement = select(User)
    return session.exec(statement).all()


def get_user_tasks(session, user_id: int):
    """READ: Get all tasks for a user"""
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()


def get_task_by_id(session, task_id: int):
    """READ: Get task by ID"""
    return session.get(Task, task_id)


def get_all_tasks(session):
    """READ: Get all tasks"""
    statement = select(Task)
    return session.exec(statement).all()


def search_tasks(session, search_term: str):
    """READ: Search tasks by keyword"""
    statement = select(Task).where(func.lower(Task.title).contains(search_term.lower()))
    return session.exec(statement).all()


# ========== UPDATE (Update data) ==========


def update_user(
    session, user_id: int, email: Optional[str] = None, username: Optional[str] = None
):
    """
    UPDATE: Update user information

    Usage:
    updated_user = update_user(session, 1, email="newemail@example.com")
    """
    # 1. Get user from database
    user = session.get(User, user_id)

    if not user:
        return None

    # 2. Update fields
    if email:
        user.email = email
    if username:
        user.username = username

    # 3. Commit
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def update_task(
    session, task_id: int, title: Optional[str] = None, status: Optional[str] = None
):
    """
    UPDATE: Update task

    Usage:
    updated_task = update_task(session, 1, title="New Title", status="in_progress")
    """
    task = session.get(Task, task_id)

    if not task:
        return None

    if title:
        task.title = title
    if status:
        task.status = status

    # updated_at is automatically updated by default_factory
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


# ========== DELETE (Delete data) ==========


def delete_user(session, user_id: int):
    """
    DELETE: Delete user

    Usage:
    delete_user(session, 1)
    """
    # 1. Get user
    user = session.get(User, user_id)

    if not user:
        return False

    # 2. Delete
    session.delete(user)

    # 3. Commit
    session.commit()

    return True


def delete_task(session, task_id: int):
    """DELETE: Delete task"""
    task = session.get(Task, task_id)

    if not task:
        return False

    session.delete(task)
    session.commit()

    return True


# ==================== 8. EXAMPLE USAGE ====================


def example_full_workflow():
    """Complete example: Create → Read → Update → Delete"""

    # Setup
    create_tables()  # Create tables

    with Session(engine) as session:
        try:
            print("\n========== CREATE ==========")
            # 1. Create user
            user = create_user(
                session, "john@example.com", "john_doe", "hashed_password_123"
            )
            print(f"Created: {user}")

            # 2. Create tasks
            task1 = create_task(session, "Learn SQLModel", "Study ORM basics", user.id)
            task2 = create_task(
                session, "Build API", "Create FastAPI endpoints", user.id
            )
            print(f"Created: {task1}")
            print(f"Created: {task2}")

            print("\n========== READ ==========")
            # 3. Get user
            fetched_user = get_user_by_id(session, user.id)
            print(f"Found: {fetched_user}")

            # 4. Get user's tasks
            user_tasks = get_user_tasks(session, user.id)
            print(f"User {user.username} has {len(user_tasks)} tasks:")
            for task in user_tasks:
                print(f"   - {task.title} ({task.status})")

            # 5. Search
            search_results = search_tasks(session, "Learn")
            print(f"Search results for 'Learn': {len(search_results)} tasks")

            print("\n========== UPDATE ==========")
            # 6. Update user
            updated_user = update_user(session, user.id, email="john.new@example.com")
            print(f"Updated: {updated_user}")

            # 7. Update task
            updated_task = update_task(session, task1.id, status="in_progress")
            print(f"Updated: {updated_task}")

            print("\n========== DELETE ==========")
            # 8. Delete task
            delete_task(session, task2.id)
            print(f"Deleted task {task2.id}")

            # 9. Delete user (will delete related tasks if CASCADE is set)
            delete_user(session, user.id)
            print(f"Deleted user {user.id}")

            # 10. Verify
            remaining_users = get_all_users(session)
            print(f"\nRemaining users: {len(remaining_users)}")

        finally:
            pass


# ==================== 9. KEY CONCEPTS ====================

"""
SQLModel:
- Models are Pydantic BaseModel + SQLAlchemy ORM combined
- Use type hints: id: int, name: str, etc.
- Use Field() for additional constraints: Field(index=True, unique=True)

Session:
- with Session(engine) as session:  → Create session
- session.add()     → Add object
- session.commit()  → Save changes
- session.delete()  → Delete object

Queries (SQLModel 2.0 style):
- session.get(User, id)  → Get by primary key
- session.exec(select(User).where(...)).first()  → Get first with filter
- session.exec(select(User)).all()  → Get all records

Filter conditions:
- User.id == 1
- User.email == "test@example.com"
- User.title.ilike("%Learn%")  → Case-insensitive search

Relationships:
- tasks: list["Task"] = Field(default=[], back_populates="owner")  → One-to-many
- owner: Optional[User] = Field(default=None, back_populates="tasks")  → Many-to-one
"""

# ==================== 10. ADVANCED EXAMPLES ====================


def advanced_queries(session):
    """Advanced queries"""

    # Filter with multiple conditions
    statement = select(User).where(
        (User.email == "john@example.com") & (User.is_active)
    )
    session.exec(statement).first()

    # Limit & Offset (pagination)
    page = 1
    limit = 10
    statement = select(User).offset((page - 1) * limit).limit(limit)
    session.exec(statement).all()

    # Count
    statement = select(User)
    len(session.exec(statement).all())

    # With relationship (eager loading)
    user_with_tasks = session.get(User, 1)
    if user_with_tasks:
        print(user_with_tasks.tasks)  # Access relationship


if __name__ == "__main__":
    # Run example
    example_full_workflow()

    # Output:
    # Tables created!
    # ========== CREATE ==========
    # Created: <User(id=1, email=john@example.com, username=john_doe)>
    # Created: <Task(id=1, title=Learn SQLModel, user_id=1)>
    # ...
