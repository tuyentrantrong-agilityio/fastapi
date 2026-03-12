from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from ..schemas.user import UserCreate, UserResponse, UserUpdate, Token, UserInDB
from ..core.hashing import verify_password
from ..core.security import create_access_token
from ..core.exceptions import UnauthorizedException
from ..dependencies.user import get_current_user, get_admin_user
from ..services.user_service import (
    create_user_service,
    get_user_by_email_service,
    update_user_profile_service,
)

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
    return await create_user_service(user)


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
    # Find user by email
    user_data = await get_user_by_email_service(form_data.username)

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
    is_admin = current_user.role == "admin"
    return await update_user_profile_service(current_user.id, user_update, is_admin)
