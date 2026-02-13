from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio

from config import settings
from models import (
    UserRegister, UserInDB, UserResponse, Token,
    TaskCreate, TaskResponse, TaskUpdate
)
from security import get_password_hash, verify_password, create_access_token
from database import fake_users_db, fake_tasks_db
import database
from dependencies import get_current_user, get_admin_user


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Task Management API with Authentication",
)


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister) -> UserResponse:
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    database.user_id_counter += 1
    
    db_user = UserInDB(
        id=database.user_id_counter,
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        created_at=datetime.utcnow()
    )
    
    fake_users_db[user.username] = db_user
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        created_at=db_user.created_at
    )


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = fake_users_db.get(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: UserResponse = Depends(get_current_user)
) -> TaskResponse:
    await asyncio.sleep(0.01)
    
    database.task_id_counter += 1
    
    new_task = {
        "id": database.task_id_counter,
        "user_id": current_user.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "completed": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    fake_tasks_db[database.task_id_counter] = new_task
    
    return TaskResponse(**new_task)


@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    current_user: UserResponse = Depends(get_current_user),
    completed: Optional[bool] = None,
    priority: Optional[str] = None
) -> List[TaskResponse]:
    await asyncio.sleep(0.01)
    
    user_tasks = [
        TaskResponse(**task) for task in fake_tasks_db.values()
        if task["user_id"] == current_user.id
    ]
    
    if completed is not None:
        user_tasks = [t for t in user_tasks if t.completed == completed]
    
    if priority is not None:
        user_tasks = [t for t in user_tasks if t.priority == priority]
    
    return user_tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: UserResponse = Depends(get_current_user)
) -> TaskResponse:
    task = fake_tasks_db.get(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if task["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    return TaskResponse(**task)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserResponse = Depends(get_current_user)
) -> TaskResponse:
    task = fake_tasks_db.get(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if task["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    update_data = task_update.dict(exclude_unset=True)
    task.update(update_data)
    task["updated_at"] = datetime.utcnow()
    
    return TaskResponse(**task)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    task = fake_tasks_db.get(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if task["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    del fake_tasks_db[task_id]
    return None


@app.get("/admin/stats")
async def get_stats(admin: UserResponse = Depends(get_admin_user)) -> dict:
    return {
        "total_users": len(fake_users_db),
        "total_tasks": len(fake_tasks_db),
        "admin": admin.username
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to Task Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
