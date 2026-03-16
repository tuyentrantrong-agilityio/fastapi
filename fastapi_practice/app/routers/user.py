from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone, timedelta

from ..schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    UserInDB,
    RefreshTokenRequest,
)
from ..core.hashing import verify_password
from ..core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    decode_token,
)
from ..core.exceptions import UnauthorizedException
from ..dependencies.user import get_current_user, get_admin_user
from ..services.user_service import (
    create_user_service,
    get_user_by_email_service,
    update_user_profile_service,
)
from ..core.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "Bad Request - Email already exists",
            "content": {
                "application/json": {"example": {"detail": "Email already registered"}}
            },
        },
        422: {
            "description": "Validation Error - Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "password"],
                                "msg": "ensure this value has at least 8 characters",
                                "type": "value_error",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
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
    Login endpoint to authenticate user and get JWT access token and opaque refresh token

    - **username**: Email address (OAuth2PasswordRequestForm uses 'username' field)
    - **password**: User password

    Returns:
        - **access_token**: JWT token (expires in 30 minutes)
        - **refresh_token**: Opaque random token (expires in 7 days)
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

    # Generate JWT access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )

    # Generate opaque refresh token
    refresh_token = generate_refresh_token()

    # Hash refresh token before storing in database
    from ..db.storage import refresh_tokens_db

    token_hash = hash_refresh_token(refresh_token)
    refresh_tokens_db[token_hash] = {
        "user_id": user_data["id"],
        "expires_at": datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "created_at": datetime.now(timezone.utc),
    }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # ← Return plain text to client
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(request: RefreshTokenRequest):
    """refresh token.

    Flow:
    1. Client sends plain text refresh token
    2. Server hashes it and looks up in database
    3. If valid and not expired → generate new tokens

    - **refresh_token**: Valid refresh token from login

    Returns:
        - **access_token**: New JWT access token
        - **refresh_token**: New opaque refresh token (plain text)
        - **token_type**: Always "bearer"

    Raises:
        401 Unauthorized: If refresh token is invalid or expired
    """
    from ..db.storage import refresh_tokens_db, users_db

    # Hash the refresh token client sent
    token_hash = hash_refresh_token(request.refresh_token)

    # Look up hashed token in database
    token_data = refresh_tokens_db.get(token_hash)

    if not token_data:
        raise UnauthorizedException("Invalid or expired refresh token")

    # Check if token has expired
    if datetime.now(timezone.utc) > token_data["expires_at"]:
        # Clean up expired token
        del refresh_tokens_db[token_hash]
        raise UnauthorizedException("Refresh token has expired")

    # Get user data
    user_id = token_data["user_id"]
    user_data = users_db.get(user_id)

    if not user_data:
        raise UnauthorizedException("User not found")

    # Generate new access token
    access_token_expires = timedelta(minutes=30)
    new_access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )

    # Generate new opaque refresh token
    new_refresh_token = generate_refresh_token()

    # Hash and save new token, revoke old one
    new_token_hash = hash_refresh_token(new_refresh_token)

    refresh_tokens_db[new_token_hash] = {
        "user_id": user_id,
        "expires_at": datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "created_at": datetime.now(timezone.utc),
    }

    # Revoke old refresh token (delete from database)
    del refresh_tokens_db[token_hash]

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


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
