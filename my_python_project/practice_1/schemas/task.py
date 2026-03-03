from pydantic import BaseModel, Field
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

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=2000, description="Task description"
    )
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation",
                "status": "todo",
            }
        }


class TaskUpdate(BaseModel):
    """Request model for updating a task"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "status": "in_progress",
            }
        }


class TaskResponse(BaseModel):
    """Response model for task"""

    id: int
    user_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation",
                "status": "in_progress",
                "created_at": "2026-03-03T10:30:00",
                "updated_at": "2026-03-03T10:30:00",
            }
        }
