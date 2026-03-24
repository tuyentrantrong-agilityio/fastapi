from app.db.base import SQLModel
from app.db.session import engine
from app.models import User, Task, Project  # Import models for metadata registration


def create_db_and_tables():
    """Create all tables in database"""
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
