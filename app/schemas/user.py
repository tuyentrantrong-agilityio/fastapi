from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "tuyen@example.com", "password": "secure_password123"}
        }
    )

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserResponse(BaseModel):
    # from_attributes=True allows Pydantic to accept ORM objects (SQLModel/SQLAlchemy)
    # and automatically map their attributes to schema fields
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"id": 1, "email": "tuyen@example.com", "role": "user"}},
    )

    id: int
    email: str
    role: str = "user"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = None


class UserInDB(UserResponse):
    """User object as stored in database (includes hashed password)"""

    hashed_password: str


class Token(BaseModel):
    """OAuth2 token response"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR...",
                "token_type": "bearer",
            }
        }
    )

    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    """Request model for refreshing access token"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR...",
            }
        }
    )

    refresh_token: str
