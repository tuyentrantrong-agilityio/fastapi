from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )

    class Config:
        schema_extra = {
            "example": {"email": "user@example.com", "password": "secure_password123"}
        }


class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True
        schema_extra = {"example": {"id": 1, "email": "user@example.com"}}


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
