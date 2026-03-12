"""User service - handles user business logic."""

from ..schemas.user import UserCreate, UserUpdate
from ..core.hashing import hash_password
from ..core.exceptions import BadRequestException, ForbiddenException
from ..db.storage import users_db, user_id_counter


async def create_user_service(user: UserCreate) -> dict:
    """
    Create a new user.

    Args:
        user: UserCreate object with email and password

    Returns:
        Dictionary with id, email, and role

    Raises:
        BadRequestException: If email already exists
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


async def get_user_by_email_service(email: str) -> dict | None:
    """
    Get user by email.

    Args:
        email: User email address

    Returns:
        User dictionary if found, None otherwise
    """
    for user in users_db.values():
        if user["email"] == email:
            return user
    return None


async def update_user_profile_service(
    user_id: int, user_update: UserUpdate, is_admin: bool
) -> dict:
    """
    Update user profile.

    Args:
        user_id: ID of the user to update
        user_update: UserUpdate object with fields to update
        is_admin: Whether the current user is an admin

    Returns:
        Updated user dictionary

    Raises:
        BadRequestException: If email already taken or invalid role
        ForbiddenException: If user tries to change role without admin access
    """
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
        current_role = users_db[user_id]["role"]
        # Only admin can change role to a different value
        if user_update.role != current_role:
            if not is_admin:
                raise ForbiddenException("Only admin users can change roles")
        if user_update.role not in ["user", "admin"]:
            raise BadRequestException("Role must be 'user' or 'admin'")
        users_db[user_id]["role"] = user_update.role

    # Return updated user
    return users_db[user_id]
