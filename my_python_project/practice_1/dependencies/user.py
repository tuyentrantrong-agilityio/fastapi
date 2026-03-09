from fastapi import Depends

from core.security import oauth2_scheme, decode_token
from core.exceptions import UnauthorizedException, ForbiddenException
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
        UnauthorizedException: If token is invalid, expired, or user not found
    """
    try:
        # Decode token to get email claim
        payload = decode_token(token)
        email: str | None = payload.get("sub")

        if email is None:
            raise UnauthorizedException("Invalid or expired credentials")

    except ValueError:
        raise UnauthorizedException("Invalid or expired credentials")

    # Find user by email in database
    user_data = None
    for user in users_db.values():
        if user["email"] == email:
            user_data = user
            break

    if user_data is None:
        raise UnauthorizedException("Invalid or expired credentials")

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
        ForbiddenException: If user is not admin
    """
    if current_user.role != "admin":
        raise ForbiddenException("Not enough permissions. Admin access required.")

    return current_user
