import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.core.config import settings

# Import SQLModel models for Alembic to detect all tables
from app.db.base import SQLModel

# Alembic Config object
config = context.config

# Set up loggers via logging config in .ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# All ORM model metadata for 'autogenerate'
target_metadata = SQLModel.metadata


# def process_revision_directives(context, revision, directives):
#     """
#     Optional: Auto-imports for migration script if needed,
#     usually not critical for basic use.
#     """
#     for directive in directives:
#         if getattr(directive, "imports", None) is None:
#             directive.imports = set()
#         directive.imports.add("from sqlalchemy import Column, Integer, String")
def process_revision_directives(context, revision, directives):
    for directive in directives:
        if getattr(directive, "imports", None) is None:
            directive.imports = set()
        directive.imports.add("import sqlmodel")


def run_migrations_offline():
    """Run Alembic migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function for online (sync/async) migration."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
        compare_type=True,  # highly recommended!
        compare_server_default=True,
        render_as_batch=False,  # PostgreSQL doesn't need batch mode
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online_async():
    """Run Alembic migrations in 'online' mode using async engine."""
    connectable = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool, echo=False)
    async with connectable.begin() as conn:
        await conn.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online_async())
