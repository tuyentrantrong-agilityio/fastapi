from fastapi import Depends, HTTPException, status

from core.security import oauth2_scheme, decode_token
from schemas.user import UserInDB
from db.storage import users_db


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header (extracted by oauth2_scheme)

    Returns:
        UserInDB: User object from database

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token to get email claim
        payload = decode_token(token)
        email: str | None = payload.get("sub")

        if email is None:
            raise credentials_exception

    except ValueError:
        raise credentials_exception

    # Find user by email in database
    user_data = None
    for user in users_db.values():
        if user["email"] == email:
            user_data = user
            break

    if user_data is None:
        raise credentials_exception

    return UserInDB(**user_data)


async def get_admin_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """
    Dependency to ensure current user is admin.

    Args:
        current_user: Current authenticated user (from get_current_user)

    Returns:
        UserInDB: User object if user is admin

    Raises:
        HTTPException 403: If user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required.",
        )

    return current_user
