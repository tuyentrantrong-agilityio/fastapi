"""Unit tests for security functions (JWT token generation and validation)."""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_token,
    generate_refresh_token,
    get_jwt_algorithm,
    hash_refresh_token,
)


class TestCreateAccessToken:
    """Test cases for create_access_token function."""

    def test_create_access_token_success(self):
        """Test successful access token creation with default expiration."""
        data = {"sub": "user@test.com"}

        token = create_access_token(data)

        # Verify token is a string
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify claims
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "user@test.com"
        assert "exp" in payload

    def test_create_access_token_with_custom_expiration(self):
        """Test access token creation with custom expiration delta."""
        data = {"sub": "user@test.com"}
        custom_expires = timedelta(hours=2)

        token = create_access_token(data, expires_delta=custom_expires)

        # Decode and verify expiration is set correctly
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)

        # Check that expiration is approximately 2 hours from now (within 10 seconds tolerance)
        time_diff = (exp_time - now).total_seconds()
        assert 7190 < time_diff < 7210  # ~2 hours


class TestDecodeToken:
    """Test cases for decode_token function."""

    def test_decode_token_success(self):
        """Test successful token decode with valid token."""
        data = {"sub": "user@test.com", "role": "user"}
        token = create_access_token(data)

        payload = decode_token(token)

        assert payload["sub"] == "user@test.com"
        assert payload["role"] == "user"

    def test_decode_token_expired(self):
        """Test decode with expired access token raises ValueError."""
        # Create token that expired 1 hour ago
        data = {"sub": "user@test.com"}
        past_expire = datetime.now(timezone.utc) - timedelta(hours=1)

        # Manually encode token with past expiration
        to_encode = data.copy()
        to_encode.update({"exp": past_expire})
        expired_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # Attempt to decode expired token
        with pytest.raises(ValueError, match="Invalid or expired token"):
            decode_token(expired_token)

    def test_decode_token_malformed(self):
        """Test decode with malformed token raises ValueError."""
        with pytest.raises(ValueError, match="Invalid or expired token"):
            decode_token("not.a.valid.token")


class TestGenerateRefreshToken:
    """Test cases for generate_refresh_token function."""

    def test_generate_refresh_token_returns_string(self):
        """Test that generate_refresh_token returns a string."""
        token = generate_refresh_token()

        assert isinstance(token, str)
        assert len(token) == 64  # 32 bytes = 64 hex characters

    def test_generate_refresh_token_unique(self):
        """Test that each call generates a unique token."""
        token1 = generate_refresh_token()
        token2 = generate_refresh_token()

        assert token1 != token2


class TestHashRefreshToken:
    """Test cases for hash_refresh_token function."""

    def test_hash_refresh_token_deterministic(self):
        """Test that hashing the same token produces the same hash."""
        token = "my_refresh_token_123"
        hash1 = hash_refresh_token(token)
        hash2 = hash_refresh_token(token)

        assert hash1 == hash2

    def test_hash_refresh_token_different_tokens(self):
        """Test that different tokens produce different hashes."""
        token1 = "token_1"
        token2 = "token_2"

        hash1 = hash_refresh_token(token1)
        hash2 = hash_refresh_token(token2)

        assert hash1 != hash2

    def test_hash_refresh_token_format(self):
        """Test that hash is valid SHA256 hex string."""
        token = generate_refresh_token()
        hashed = hash_refresh_token(token)

        # SHA256 produces 64 hex characters
        assert len(hashed) == 64
        assert all(c in "0123456789abcdef" for c in hashed)


class TestGetJwtAlgorithm:
    """Test cases for get_jwt_algorithm function."""

    def test_get_jwt_algorithm_returns_supported(self):
        """Test that get_jwt_algorithm returns a supported algorithm."""
        algorithm = get_jwt_algorithm()

        assert algorithm in {"HS256", "HS384", "HS512"}
