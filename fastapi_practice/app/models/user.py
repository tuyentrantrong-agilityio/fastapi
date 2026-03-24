from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.models.task import Task


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = "user"
    is_active: bool = True
    tasks: list["Task"] = Relationship(back_populates="user")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
