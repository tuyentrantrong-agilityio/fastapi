"""User service - handles user business logic."""

import email

from ..schemas.user import UserCreate, UserUpdate
from ..core.hashing import hash_password
from ..core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from sqlmodel import Session, select
from ..models.user import User


async def create_user_service(session: Session, user: UserCreate) -> User:
    """
    Create a new user.

    Args:
        user: UserCreate object with email and password

    Returns:
        User object with id, email, hashed_password and role

    Raises:
        BadRequestException: If email already exists
    """
    # Check if email already exists
    statement = select(User).where(User.email == user.email)
    result = session.exec(statement).first()
    if result:
        raise BadRequestException("Email already registered")
    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role="user",
    )

    # Create new user
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


async def get_user_by_email_service(session: Session, email: str) -> User | None:
    """
    Get user by email.

    Args:
        email: User email address

    Returns:
        User object if found, None otherwise
    """

    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


async def update_user_profile_service(
    session: Session, user_id: int, user_update: UserUpdate, is_admin: bool
) -> User:
    """
    Update user profile.

    Args:
        user_id: ID of the user to update
        user_update: UserUpdate object with fields to update
        is_admin: Whether the current user is an admin

    Returns:
        Updated user object

    Raises:
        BadRequestException: If email already taken or invalid role
        ForbiddenException: If user tries to change role without admin access
    """

    user = session.get(User, user_id)
    if not user:
        raise NotFoundException("User not found")

    # Update email if provided
    if user_update.email is not None and user_update.email != user.email:
        statement = select(User).where(
            (User.email == user_update.email) & (User.id != user_id)
        )
        if session.exec(statement).first():
            raise BadRequestException("Email already taken")
        user.email = user_update.email

    # Update password if provided
    if user_update.password is not None:
        user.hashed_password = hash_password(user_update.password)

    # Update role if provided
    if user_update.role is not None and user_update.role != user.role:
        if user_update.role not in ["user", "admin"]:
            raise BadRequestException("Role must be 'user' or 'admin'")
        if user_update.role != user.role and not is_admin:
            raise ForbiddenException("Only admin users can change roles")
        user.role = user_update.role

    # Save changes
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
