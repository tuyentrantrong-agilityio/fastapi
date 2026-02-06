"""
HTTP BASIC AUTH - QUICK REFERENCE

What: Simple username + password authentication via HTTP header
Browser shows login popup automatically when receiving 401 response

BASIC EXAMPLE
"""

from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
security = HTTPBasic()


# Example 1: Simple (no validation) - just return credentials
@app.get("/users/me")
def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """Browser auto-sends: Authorization: Basic base64(username:password)"""
    return {"username": credentials.username}


# Example 2: Proper validation (RECOMMENDED)
def validate_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """
    Use secrets.compare_digest() to prevent timing attacks
    (must compare full string, not byte-by-byte like ==)
    """
    correct_username = b"admin"
    correct_password = b"password123"

    current_username = credentials.username.encode("utf-8")
    current_password = credentials.password.encode("utf-8")

    is_user_ok = secrets.compare_digest(current_username, correct_username)
    is_pass_ok = secrets.compare_digest(current_password, correct_password)

    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},  # Tell browser to show login popup
        )

    return credentials.username


@app.get("/secure")
def secure_endpoint(username: Annotated[str, Depends(validate_credentials)]):
    return {"username": username}


"""
KEY CONCEPTS:

1. HTTPBasic() = tells FastAPI to use HTTP Basic Auth

2. Depends(security) = FastAPI extracts & decodes Authorization header

3. credentials.username, credentials.password = already decoded

4. secrets.compare_digest() = safe comparison (same time every time)

5. WWW-Authenticate header = signals browser to show login popup

WHEN TO USE:
Yes: Internal APIs, admin tools, scripts
No: Public APIs, mobile apps, user apps (use JWT/OAuth2 instead)

IMPORTANT: Always use HTTPS! Base64 is NOT encryption.
"""
