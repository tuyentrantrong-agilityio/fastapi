from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="todo")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="tasks")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="tasks")
