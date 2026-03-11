from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from ..schemas.user import UserCreate, UserResponse, UserUpdate, Token, UserInDB
from ..core.hashing import hash_password, verify_password
from ..core.security import create_access_token
from ..core.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
)
from ..dependencies.user import get_current_user, get_admin_user
from ..db.storage import users_db, user_id_counter

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
            raise BadRequestException("Email already registered")

    # Create new user
    user_id = user_id_counter["id"]
    user_id_counter["id"] += 1

    hashed_password = hash_password(user.password)

    users_db[user_id] = {
        "id": user_id,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_active": True,
        "role": "user",  # Default role is 'user'
    }

    return {"id": user_id, "email": user.email, "role": "user"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint to authenticate user and get JWT access token.

    - **username**: Email address (OAuth2PasswordRequestForm uses 'username' field)
    - **password**: User password

    Returns:
        - **access_token**: JWT token to use for authenticated requests
        - **token_type**: Always "bearer"

    Raises:
        401 Unauthorized: If email not found or password invalid
    """
    # Find user by email (OAuth2PasswordRequestForm uses 'username' field)
    user_data = None
    for uid, user in users_db.items():
        if user["email"] == form_data.username:
            user_data = user
            break

    # Validate credentials
    if not user_data or not verify_password(
        form_data.password, user_data["hashed_password"]
    ):
        raise UnauthorizedException("Invalid email or password")

    # Generate JWT token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current user's profile.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Returns:
        User profile (id, email, role)
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate, current_user: UserInDB = Depends(get_current_user)
):
    """
    Update current user's profile.

    Requires:
        - Valid JWT token in Authorization header (Bearer token)

    Update fields:
        - **email**: Optional new email address
        - **password**: Optional new password (min 8 characters)
        - **role**: Optional role change (only admin can change roles)

    Returns:
        Updated user profile
    """
    user_id = current_user.id

    # Update email if provided
    if user_update.email is not None:
        # Check if email already exists
        for uid, user_data in users_db.items():
            if uid != user_id and user_data["email"] == user_update.email:
                raise BadRequestException("Email already taken")
        users_db[user_id]["email"] = user_update.email

    # Update password if provided
    if user_update.password is not None:
        users_db[user_id]["hashed_password"] = hash_password(user_update.password)

    # Update role if provided (only admin can change roles to different value)
    if user_update.role is not None:
        # Only admin can change role to a different value
        if user_update.role != current_user.role:
            if current_user.role != "admin":
                raise ForbiddenException("Only admin users can change roles")
        if user_update.role not in ["user", "admin"]:
            raise BadRequestException("Role must be 'user' or 'admin'")
        users_db[user_id]["role"] = user_update.role

    # Return updated user
    return users_db[user_id]
