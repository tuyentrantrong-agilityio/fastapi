from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..core.exceptions import ForbiddenException, UnauthorizedException
from ..core.security import decode_token, oauth2_scheme
from ..db.session import get_async_session
from ..models.user import User
from ..schemas.user import UserInDB


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    token: str = Depends(oauth2_scheme),
) -> UserInDB:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        session: AsyncSession for database operations
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
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user_data = result.scalars().first()

    if user_data is None:
        raise UnauthorizedException("Invalid or expired credentials")

    # Convert SQLModel object to Pydantic schema using from_attributes=True
    # This automatically maps User.id, User.email, User.role, User.hashed_password
    return UserInDB.model_validate(user_data)


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
