from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets
import hashlib
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .config import settings

# OAuth2 scheme - tells FastAPI where to find the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

SUPPORTED_JWT_ALGORITHMS = {"HS256", "HS384", "HS512"}


def get_jwt_algorithm() -> str:
    alg = str(settings.ALGORITHM or "").strip().upper()
    if alg not in SUPPORTED_JWT_ALGORITHMS:
        # If config has invalid algorithm, fallback to secure default.
        print(
            f"[WARNING] Invalid JWT algorithm '{settings.ALGORITHM}' from config. Using 'HS256' instead."
        )
        return "HS256"
    return alg


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary with claims (e.g., {"sub": "user@example.com"})
        expires_delta: Optional expiration time delta from now

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # Encode JWT
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def generate_refresh_token() -> str:
    """
    Generate a secure opaque random refresh token.

    Returns a random 64-character hexadecimal string that doesn't contain
    any user data. This is stored server-side (hashed) for lookup and revocation.

    Returns:
        str: Random 64-character hexadecimal string (plain text to return to client)
    """
    return secrets.token_hex(32)  # 64 character hex string


def hash_refresh_token(token: str) -> str:
    """
    Hash a refresh token using SHA256 (deterministic hashing).

    Used for storing refresh tokens in database. Unlike password hashing (Argon2),
    this is deterministic so we can compare tokens directly.

    Args:
        token: Plain text refresh token from generate_refresh_token()

    Returns:
        str: SHA256 hash of the token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload (dictionary with claims)

    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")
