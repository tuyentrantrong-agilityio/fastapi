from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from schemas.user import UserCreate, UserResponse
from core.hashing import hash_password
from db.storage import users_db, user_id_counter

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user: UserCreate):
    """
    Register a new user.

    - **email**: Valid email address (must be unique)
    - **password**: At least 8 characters long

    Returns: User ID and email
    """
    # Check if email already exists
    for user_data in users_db.values():
        if user_data["email"] == user.email:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Email already registered"},
            )

    # Create new user
    user_id = user_id_counter["id"]
    user_id_counter["id"] += 1

    hashed_password = hash_password(user.password)

    users_db[user_id] = {
        "id": user_id,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_active": True,
    }

    return {"id": user_id, "email": user.email}
