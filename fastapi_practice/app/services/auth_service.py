"""Auth service - handles authentication business logic."""

from datetime import datetime, timedelta
from typing import Dict, cast

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.hashing import verify_password
from ..core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from ..core.exceptions import UnauthorizedException
from ..core.config import settings
from ..models.refresh_token import RefreshToken
from ..models.user import User

# from ..db.storage import users_db, refresh_tokens_db
from .user_service import get_user_by_email_service


async def login_service(
    session: AsyncSession, email: str, password: str
) -> Dict[str, str]:
    """
    Authenticate user and generate tokens.

    Args:
        session: AsyncSession for database operations
        email: User email address
        password: User password (plain text)

    Returns:
        Dictionary with access_token, refresh_token, and token_type

    Raises:
        UnauthorizedException: If email not found or password is invalid
    """
    # Find user by email
    user_data = await get_user_by_email_service(session, email)

    # Validate credentials (email exists and password matches)
    if not user_data or not verify_password(password, user_data.hashed_password):
        raise UnauthorizedException("Invalid email or password")

    # Generate JWT access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_data.email}, expires_delta=access_token_expires
    )

    # Generate opaque refresh token
    refresh_token = generate_refresh_token()

    # Hash and store refresh token in database
    token_hash = hash_refresh_token(refresh_token)
    if user_data.id is None:
        raise ValueError("User ID missing")
    refresh_tokens = RefreshToken(
        user_id=user_data.id,
        # user cast to int, dont check condition user_data.id is None
        # user_id=cast(int, user_data.id),
        token_hash=token_hash,
        expires_at=datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session.add(refresh_tokens)
    await session.commit()
    await session.refresh(refresh_tokens)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # Return plain text to client
        "token_type": "bearer",
    }


async def refresh_access_token_service(
    session: AsyncSession, refresh_token: str
) -> Dict[str, str]:
    """
    Refresh access token using refresh token.

    Flow:
    1. Hash the refresh token client sent
    2. Look up hashed token in database
    3. Validate token exists and not expired
    4. Generate new tokens (access + refresh)
    5. Revoke old refresh token

    Args:
        session: AsyncSession for database operations
        refresh_token: Valid refresh token from login (plain text)

    Returns:
        Dictionary with new access_token, refresh_token, and token_type

    Raises:
        UnauthorizedException: If refresh token is invalid or expired
    """
    # Hash the refresh token client sent and look up in database
    token_hash = hash_refresh_token(refresh_token)
    # statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    # result = await session.execute(statement)
    # token_data = result.scalars().first()
    statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await session.execute(statement)
    token_data = result.scalars().first()

    if not token_data:
        raise UnauthorizedException("Invalid or expired refresh token")
    expires_at = token_data.expires_at
    # Check if token has expired
    if datetime.now() > expires_at:
        # Persist deleted token
        await session.delete(token_data)
        # TODO: For audit trail, mark as revoked instead of delete:
        # token_data.is_revoked = True
        # session.add(token_data)
        # session.commit()
        await session.commit()
        raise UnauthorizedException("Refresh token has expired")

    # Get user associated with token
    user_id = token_data.user_id
    user_data = token_data.user

    if not user_data:
        raise UnauthorizedException("User not found")

    # Generate new access token
    access_token_expires = timedelta(minutes=30)
    new_access_token = create_access_token(
        data={"sub": user_data.email}, expires_delta=access_token_expires
    )

    # Generate new refresh token
    new_refresh_token = generate_refresh_token()

    # Hash and save new refresh token
    new_token_hash = hash_refresh_token(new_refresh_token)
    new_refresh_token_record = RefreshToken(
        user_id=user_id,
        token_hash=new_token_hash,
        expires_at=datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Revoke old refresh token and create new one in single transaction
    await session.delete(token_data)
    session.add(new_refresh_token_record)
    await session.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
