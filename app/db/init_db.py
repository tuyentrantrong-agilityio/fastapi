"""Initialize database and create tables."""

from app.db.base import SQLModel
from app.db.session import engine


async def create_db_and_tables():
    """Create all tables in database asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
