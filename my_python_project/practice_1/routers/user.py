from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from schemas.user import UserCreate, UserResponse
from core.hashing import hash_password, verify_password
from core.security import create_access_token
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


@router.post("/login")
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
