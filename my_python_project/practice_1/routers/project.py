from fastapi import APIRouter, status, Depends
from datetime import datetime, timezone
from typing import List

from schemas.project import ProjectCreate, ProjectResponse
from schemas.user import UserInDB
from dependencies.user import get_current_user
from db.storage import projects_db, project_id_counter

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new project for current user.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Args:
        project: ProjectCreate object containing name and optional description
        current_user: Current authenticated user (auto-injected)

    Returns:
        Created project with id, user_id, timestamps, etc.
    """
    project_id = project_id_counter["id"]
    project_id_counter["id"] += 1

    now = datetime.now(timezone.utc)

    projects_db[project_id] = {
        "id": project_id,
        "user_id": current_user.id,
        "name": project.name,
        "description": project.description,
        "created_at": now,
        "updated_at": now,
    }

    return projects_db[project_id]


@router.get("/", response_model=List[ProjectResponse])
async def get_all_projects(current_user: UserInDB = Depends(get_current_user)):
    """
    Get all projects belonging to current user.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Returns:
        List of ProjectResponse objects for current user
    """
    user_projects = [
        project
        for project in projects_db.values()
        if project["user_id"] == current_user.id
    ]
    return user_projects
