from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not all(c.isalnum() or c in '_-' for c in v):
            raise ValueError('Username must be alphanumeric with underscores/hyphens only')
        return v


class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    created_at: datetime


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(default="medium")
    
    @validator('priority')
    def priority_valid(cls, v):
        valid_priorities = ['low', 'medium', 'high']
        if v.lower() not in valid_priorities:
            raise ValueError(f'Priority must be one of {valid_priorities}')
        return v.lower()


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = None
    completed: Optional[bool] = None
