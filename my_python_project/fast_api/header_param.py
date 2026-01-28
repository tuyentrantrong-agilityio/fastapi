"""
FastAPI Header Parameters

Header is information sent along with request (like metadata)
- User-Agent: browser type
- Authorization: token for authentication
- Content-Type: data type being sent
- X-Custom-Header: custom info

When client calls API, headers look like this:
GET /items/
User-Agent: Mozilla/5.0
Authorization: Bearer token123
"""

from typing import Annotated
from fastapi import FastAPI, Header

app = FastAPI()


# ============================================================
# 1. GET SINGLE HEADER
# ============================================================


@app.get("/user-info/")
async def get_user_info(user_agent: Annotated[str | None, Header()] = None):
    """
    Get User-Agent from request header

    Header in request:
        User-Agent: Mozilla/5.0

    Response:
        {"User-Agent": "Mozilla/5.0"}

    Note: user_agent (with _) automatically maps to User-Agent (with -)
    """
    return {"User-Agent": user_agent}


# ============================================================
# 2. REQUIRED HEADER
# ============================================================


@app.get("/secure/")
async def secure_endpoint(x_token: Annotated[str, Header()]):
    """
    Required header - if not sent will error 422

    Header in request:
        X-Token: secret-token-123

    Response:
        {"X-Token": "secret-token-123"}
    """
    return {"X-Token": x_token}


# ============================================================
# 3. MULTIPLE HEADERS WITH DEFAULTS
# ============================================================


@app.get("/profile/")
async def get_profile(
    user_agent: Annotated[str | None, Header()] = None,
    x_token: Annotated[str | None, Header()] = None,
    accept: Annotated[str | None, Header()] = None,
):
    """
    Get multiple headers at once

    These headers are optional (have default = None)
    """
    return {
        "User-Agent": user_agent,
        "X-Token": x_token,
        "Accept": accept,
    }


# ============================================================
# 4. DUPLICATE HEADERS (Duplicate Headers - List)
# ============================================================


@app.get("/tokens/")
async def get_tokens(x_token: Annotated[list[str] | None, Header()] = None):
    """
    Client can send same header multiple times:
        X-Token: token1
        X-Token: token2
        X-Token: token3

    Response:
        {"X-Token": ["token1", "token2", "token3"]}
    """
    return {"X-Token": x_token}


# ============================================================
# 5. HEADER AUTO UNDERSCORE CONVERSION
# ============================================================


@app.get("/custom/")
async def get_custom(
    my_custom_header: Annotated[str | None, Header()] = None,
):
    """
    Variable my_custom_header automatically becomes My-Custom-Header

    FastAPI conversion rules:
        my_custom_header -> My-Custom-Header
        x_token -> X-Token
        user_agent -> User-Agent

    This is HTTP header naming standard
    """
    return {"My-Custom-Header": my_custom_header}


# ============================================================
# 6. DISABLE AUTO CONVERSION (Not Recommended)
# ============================================================


@app.get("/exact-header/")
async def get_exact_header(
    x_token: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    """
    convert_underscores=False -> keep x_token as is (don't convert to X-Token)

    ⚠️ Not recommended because:
    - Many servers/proxies block headers with underscores
    - HTTP standard uses hyphens (-)

    Only use if legacy backend requires it
    """
    return {"x_token": x_token}


# ============================================================
# 7. DESCRIPTION AND METADATA
# ============================================================


@app.get("/with-description/")
async def get_with_description(
    x_token: Annotated[
        str | None,
        Header(description="Token for user authentication"),
    ] = None,
):
    """
    Add description for header in docs

    Description will show in Swagger UI (/docs)
    helps API users understand what this header does
    """
    return {"X-Token": x_token}


# ============================================================
# 8. AUTHORIZATION - MOST IMPORTANT HEADER
# ============================================================


@app.get("/me/")
async def get_me(
    authorization: Annotated[str | None, Header()] = None,
):
    """
    Authorization header - for authenticating users

    Client sends:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Backend uses token to:
        1. Check token is valid
        2. Decode token to get user_id
        3. Check permissions

    This is foundation of login/authentication system
    """
    if authorization is None:
        return {"error": "Authorization header required"}

    return {"authorization": authorization}


# ============================================================
# 9. MULTIPLE HEADERS (Real-World Example)
# ============================================================


@app.get("/api/data/")
async def get_api_data(
    authorization: Annotated[
        str | None,
        Header(description="Bearer token"),
    ] = None,
    user_agent: Annotated[
        str | None,
        Header(description="Browser type"),
    ] = None,
    x_request_id: Annotated[
        str | None,
        Header(description="ID to trace request"),
    ] = None,
):
    """
    Real-world - API receives multiple headers at once

    Example:
    GET /api/data/
    Authorization: Bearer token123
    User-Agent: Mozilla/5.0
    X-Request-ID: req-123-456

    Backend handles:
    - authorization: check who is user
    - user_agent: log client type
    - x_request_id: trace request in logs
    """
    return {
        "message": "Your data",
        "request_id": x_request_id,
        "browser": user_agent,
    }


# ============================================================
# SUMMARY
# ============================================================
"""
✓ Header is information sent with request (metadata)
✓ Common: Authorization, User-Agent, X-Custom
✓ FastAPI auto converts user_agent -> User-Agent
✓ Headers optional use = None
✓ Can receive duplicate headers using list[str]
✓ Authorization is most important header (authentication)
✓ Headers in docs help API users understand better
"""
