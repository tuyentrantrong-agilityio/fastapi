"""Database session configuration with async support."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Ensure DATABASE_URL has +asyncpg driver (Railway may not include it)
database_url = settings.DATABASE_URL
if database_url and "postgresql://" in database_url and "+asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with PostgreSQL
engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    poolclass=NullPool,
)

# # Create async session factory
# async_session_maker = async_sessionmaker(
#     engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autoflush=False,
# )

# Create async session local class
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# async def get_async_session() -> AsyncSession:
#     """
#     Dependency to get async database session.

#     Yields an AsyncSession and automatically closes it after the request.


#     Usage in routers:
#         @router.get("/")
#         async def my_endpoint(session: AsyncSession = Depends(get_async_session)):
#             ...
#     """
#     async with async_session_maker() as session:
#         yield session
async def get_async_session():
    """Yield an async database session and close it after the request."""
    async with AsyncSessionLocal() as session:
        yield session
