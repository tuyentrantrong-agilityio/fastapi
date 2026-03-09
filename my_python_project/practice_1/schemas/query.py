from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class SortDirection(str, Enum):
    """Sort direction enum"""

    ASC = "asc"
    DESC = "desc"


class TaskFilterParams(BaseModel):
    """Query parameters for filtering and searching tasks"""

    status: Optional[str] = Field(
        None,
        description="Filter by status (comma-separated for multiple, e.g., 'todo,in_progress')",
    )
    search: Optional[str] = Field(
        None,
        description="Search in title and description (case-insensitive)",
    )
    search_fields: Optional[str] = Field(
        "title,description",
        description="Fields to search in (comma-separated): title, description, or both",
    )
    sort_by: Optional[str] = Field(
        "created_at",
        description="Sort by field: created_at, title, status, updated_at",
    )
    sort_direction: Optional[SortDirection] = Field(
        SortDirection.DESC, description="Sort direction: asc or desc"
    )
    page: Optional[int] = Field(1, ge=1, description="Page number (1-based)")
    limit: Optional[int] = Field(
        10, ge=1, le=100, description="Items per page (max 100)"
    )

    @field_validator("status")
    def validate_status(cls, v):
        if v is None:
            return None
        # Accept comma-separated values
        valid_statuses = ["todo", "in_progress", "done"]
        statuses = [s.strip() for s in v.split(",")]
        for status in statuses:
            if status not in valid_statuses:
                raise ValueError(
                    f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                )
        return v

    @field_validator("sort_by")
    def validate_sort_by(cls, v):
        valid_fields = ["created_at", "title", "status", "updated_at"]
        if v not in valid_fields:
            raise ValueError(
                f"Invalid sort_by '{v}'. Must be one of: {', '.join(valid_fields)}"
            )
        return v

    @field_validator("search_fields")
    def validate_search_fields(cls, v):
        valid_fields = ["title", "description"]
        fields = [f.strip() for f in v.split(",")]
        for field in fields:
            if field not in valid_fields:
                raise ValueError(
                    f"Invalid search field '{field}'. Must be one of: {', '.join(valid_fields)}"
                )
        return v


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    total: int = Field(..., description="Total items matching filters")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_more: bool = Field(..., description="Whether there are more pages")

    class Config:
        schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "limit": 10,
                "pages": 10,
                "has_more": True,
            }
        }