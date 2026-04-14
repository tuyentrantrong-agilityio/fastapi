from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    UserInDB,
    RefreshTokenRequest,
)
from ..dependencies.user import get_current_user, get_admin_user
from ..db.session import get_async_session
from ..services.user_service import (
    create_user_service,
    update_user_profile_service,
)
from ..services.auth_service import (
    login_service,
    refresh_access_token_service,
)
from ..tasks.email_tasks import send_welcome_email_task

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
async def register(
    user: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Register a new user and send welcome email via Celery.

    - **email**: Valid email address (must be unique)
    - **password**: At least 8 characters long

    Returns: User ID and email
    """
    new_user = await create_user_service(session, user)
    # Queue email task via Celery (returns immediately)
    send_welcome_email_task.delay(email=new_user.email, user_name=new_user.email)
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
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
    return await login_service(session, form_data.username, form_data.password)


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Refresh access token using refresh token.

    Flow:
    1. Client sends plain text refresh token
    2. Server hashes it and looks up in database
    3. If valid and not expired -> generate new tokens

    - **refresh_token**: Valid refresh token from login

    Returns:
        - **access_token**: New JWT access token
        - **refresh_token**: New opaque refresh token (plain text)
        - **token_type**: Always "bearer"

    Raises:
        401 Unauthorized: If refresh token is invalid or expired
    """
    return await refresh_access_token_service(session, request.refresh_token)


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
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
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
    return await update_user_profile_service(
        session, current_user.id, user_update, is_admin
    )
