from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    """Request model for creating a project"""

    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(
        None, max_length=2000, description="Project description"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "FastAPI Learning",
                "description": "Complete FastAPI practice project",
            }
        }


class ProjectUpdate(BaseModel):
    """Request model for updating a project"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "FastAPI Advanced",
                "description": "Advanced FastAPI concepts",
            }
        }


class ProjectResponse(BaseModel):
    """Response model for project"""

    id: int
    user_id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "name": "FastAPI Learning",
                "description": "Complete FastAPI practice project",
                "created_at": "2026-03-06T10:30:00",
                "updated_at": "2026-03-06T10:30:00",
            }
        }
