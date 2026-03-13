from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    """Task status enum"""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    """Request model for creating a task"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation",
                "status": "todo",
            }
        }
    )

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=2000, description="Task description"
    )
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")


class TaskUpdate(BaseModel):
    """Request model for updating a task"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Complete project documentation",
                "status": "in_progress",
            }
        }
    )

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    """Response model for task"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation",
                "status": "in_progress",
                "project_id": 1,
                "created_at": "2026-03-03T10:30:00",
                "updated_at": "2026-03-03T10:30:00",
            }
        },
    )

    id: int
    user_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    project_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
