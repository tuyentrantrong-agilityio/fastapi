"""
GET_CURRENT_USER - Extract User from Token

Problem: First security example only returns token, but apps need user info
Token "abc123" → User { username, email, full_name }

Goal: Write endpoint that receives User directly (not token)
@app.get("/users/me")
async def read_users_me(current_user: User):  # Get User, not token
    return current_user
"""

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Annotated


# ==============================================================================
# 1. USER MODEL - What is User?
# ==============================================================================
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


# Why User model?
# - Token = simple string "abc123"
# - App needs = username, email, full_name, disabled
# - Pydantic validates + autocomplete + clear types


# ==============================================================================
# 2. DECODE LOGIC - Fake decoder (real JWT later)
# ==============================================================================
def fake_decode_token(token: str) -> User:
    """Convert token -> User (simplified, real version uses JWT)"""
    return User(
        username=f"user_from_{token}", email="john@example.com", full_name="John Doe"
    )


# ==============================================================================
# 3. THE KEY DEPENDENCY - Token to User conversion
# ==============================================================================
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    MOST IMPORTANT DEPENDENCY
    Input: token from header
    Output: User object

    This dependency:
    - Gets token (from oauth2_scheme)
    - Decodes token -> User
    - Returns User (not token)
    """
    user = fake_decode_token(token)
    return user


# ==============================================================================
# 4. FLOW WHEN REQUEST COMES IN
# ==============================================================================
# Request: GET /users/me with Authorization: Bearer abc123
#
# FastAPI flow:
#   1. oauth2_scheme → extract "abc123" from header
#   2. get_current_user(token="abc123") called
#   3. fake_decode_token("abc123") → User object
#   4. Inject User into read_users_me
#   5. Endpoint receives User, not token!


# ==============================================================================
# 5. ENDPOINT - ENDPOINT DOESN'T HANDLE SECURITY
# ==============================================================================
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get current user info.
    Endpoint is SIMPLE - dependency handles all security.
    """
    return current_user


@app.get("/users/{username}")
async def read_user(
    username: str, current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Any protected endpoint - just add Depends(get_current_user)
    All 1000+ endpoints can reuse same dependency!
    """
    return {"user": username, "current_user": current_user}


@app.get("/public")
async def public_route():
    """No Depends() = no token required"""
    return {"message": "No token needed"}


# ==============================================================================
# USAGE & KEY CONCEPTS
# ==============================================================================

# CURL EXAMPLES:
# 1. Get token (requires login endpoint):
#    curl -X POST http://localhost:8000/login \
#         -H "Content-Type: application/x-www-form-urlencoded" \
#         -d "username=john&password=secret"
#
# 2. Use token to access protected route:
#    curl http://localhost:8000/users/me \
#         -H "Authorization: Bearer <token>"
#
# Response: { "username": "user_from_<token>", "email": "john@example.com", ... }


# FORMULA TO REMEMBER:
# oauth2_scheme ──→ extracts token from header
# get_current_user ─→ token → User (dependency handles all security)
# endpoint ────→ receives User (never sees token)


# WHY THIS IS GREAT:
# Write security logic ONCE in get_current_user
# Use in 1000+ endpoints without repeating code
# Change to JWT/database? Only edit get_current_user
# Endpoints stay SIMPLE - just focus on business logic


# CRITICAL PRINCIPLE:
# "Endpoints don't handle security - dependencies do all the work"
