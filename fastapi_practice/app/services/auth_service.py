"""Auth service - handles authentication business logic."""

from datetime import datetime, timezone, timedelta
from typing import Dict

from ..core.hashing import verify_password
from ..core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from ..core.exceptions import UnauthorizedException
from ..core.config import settings
from ..db.storage import users_db, refresh_tokens_db
from .user_service import get_user_by_email_service


async def login_service(email: str, password: str) -> Dict[str, str]:
    """
    Authenticate user and generate tokens.

    Args:
        email: User email address
        password: User password (plain text)

    Returns:
        Dictionary with access_token, refresh_token, and token_type

    Raises:
        UnauthorizedException: If email not found or password is invalid
    """
    # Find user by email
    user_data = await get_user_by_email_service(email)

    # Validate credentials
    if not user_data or not verify_password(password, user_data["hashed_password"]):
        raise UnauthorizedException("Invalid email or password")

    # Generate JWT access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )

    # Generate opaque refresh token
    refresh_token = generate_refresh_token()

    # Hash and store refresh token in database
    token_hash = hash_refresh_token(refresh_token)
    refresh_tokens_db[token_hash] = {
        "user_id": user_data["id"],
        "expires_at": datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "created_at": datetime.now(timezone.utc),
    }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # Return plain text to client
        "token_type": "bearer",
    }


async def refresh_access_token_service(refresh_token: str) -> Dict[str, str]:
    """
    Refresh access token using refresh token.

    Flow:
    1. Hash the refresh token client sent
    2. Look up hashed token in database
    3. Validate token exists and not expired
    4. Generate new tokens (access + refresh)
    5. Revoke old refresh token

    Args:
        refresh_token: Valid refresh token from login (plain text)

    Returns:
        Dictionary with new access_token, refresh_token, and token_type

    Raises:
        UnauthorizedException: If refresh token is invalid or expired
    """
    # Hash the refresh token client sent
    token_hash = hash_refresh_token(refresh_token)

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

    # Hash and save new token
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
