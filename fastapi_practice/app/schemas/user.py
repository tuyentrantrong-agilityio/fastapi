from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "secure_password123"}
        }


class UserResponse(BaseModel):
    id: int
    email: str
    role: str = "user"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {"id": 1, "email": "user@example.com", "role": "user"}
        }


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = None


class UserInDB(UserResponse):
    """User object as stored in database (includes hashed password)"""

    hashed_password: str


class Token(BaseModel):
    """OAuth2 token response"""

    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
                "token_type": "bearer",
            }
        }
