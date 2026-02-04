"""
SECURITY - Authentication and Authorization in FastAPI

Problem: If anyone calls DELETE /user -> everyone deleted
Security answers 2 questions:
  1. Who are you? (Authentication)
  2. Are you allowed? (Authorization)

Analogy: Movie theater ticket
  - Buy ticket ONCE
  - Show ticket MANY times
  - Just valid ticket = access granted

Same for API:
  - Username + password = 1 time at login
  - Token = every request after login
  - Just valid token = access granted
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime

# ==============================================================================
# COMPLETE WORKING CODE
# ==============================================================================

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Mock data
fake_users = {"john": {"password": "secret123"}}
tokens_store = {}


def create_token(username: str) -> str:
    """Generate token - in production use JWT"""
    token = f"{username}-token-{datetime.now().isoformat()}"
    tokens_store[token] = username
    return token


def verify_token(token: str) -> str | None:
    """Check if token is valid"""
    return tokens_store.get(token)


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Step 1: Login with username/password -> Get token"""
    user = fake_users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected")
async def protected_route(token: Annotated[str, Depends(oauth2_scheme)]):
    """Step 2: Use token to access protected endpoint"""
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": f"Hello {username}"}


@app.get("/users/me")
async def get_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get current user (also protected)"""
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": username}


# USAGE:
# curl -X POST http://localhost:8000/login -d "username=john&password=secret123"
# -> Get token
# curl -X GET http://localhost:8000/protected -H "Authorization: Bearer [token]"
# -> See protected data


# ==============================================================================
# KEY CONCEPTS
# ==============================================================================

# PASSWORD FLOW (OAuth2):
#   1. User: username + password -> /login
#   2. Server: validate -> return token
#   3. User: token -> /protected
#   4. Server: validate token -> return data

# TOKEN:
#   - String: [Header].[Payload].[Signature]
#   - Tells server: who user is, what permissions they have, when expires
#   - JWT example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# BEARER TOKEN:
#   - "Whoever has this token can access"
#   - Send as: Authorization: Bearer <token>

# HTTPS:
#   - OAuth2 itself doesn't encrypt, just rules
#   - HTTPS encrypts token/password in transit
#   - Rule: Always use HTTPS with OAuth2 in production

# FASTAPI AUTOMATES:
#   - OAuth2PasswordBearer: extracts token from Authorization header
#   - Depends(oauth2_scheme): enforces token requirement
#   - Auto-returns 401 if token missing
#   - Auto-generates "Authorize" button in Swagger

# HTTP STATUS CODES:
#   - 401 Unauthorized: Missing or invalid token
#   - 403 Forbidden: Valid token but no permission
#   - 200 OK: Valid token and authorized

# NEXT STEPS:
#   - Use JWT library for real tokens (not simple strings)
#   - Hash passwords with bcrypt (never store plain text)
#   - Add token expiration
#   - Implement permission/authorization checks
