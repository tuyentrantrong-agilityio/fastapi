"""
SECURITY FIRST STEP - Basic token requirement in FastAPI

Real problem:
  Frontend (React/Vue/Mobile) cannot call API freely
  Must login first -> Get token -> Use token for other API calls

Key:
  Token = string representing authenticated user
  Frontend sends token in: Authorization: Bearer <token>
  If no token -> API returns 401 Unauthorized

OAuth2 = Standard way to handle this
  We use: Password Flow + Bearer Token
"""

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

# ==============================================================================
# Step 1: Create OAuth2 scheme
# ==============================================================================

"""
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

What this does:
  - Tells FastAPI this app uses OAuth2 Password Flow
  - "token" = endpoint where frontend gets token (not created yet)
  - Generates "Authorize" button in Swagger automatically
  - Tells frontend where to login

What it DOESN'T do:
  - Doesn't create /token endpoint
  - Doesn't validate password
  - Doesn't generate real tokens yet
  - Just declares the scheme
"""


# ==============================================================================
# Step 2: Require token for endpoint
# ==============================================================================

"""
from fastapi import Depends

@app.get("/items/")
async def read_items(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    return {"token": token}

What Depends(oauth2_scheme) does:
  1. FastAPI looks for Authorization header
  2. Extracts Bearer <token> part
  3. If missing -> Return 401 Unauthorized automatically
  4. If present -> Pass token to function

If function reaches: token parameter is guaranteed to exist
No need to check yourself
"""


# ==============================================================================
# Step 3: Test it
# ==============================================================================

"""
Request WITHOUT token:
  GET /items/
  
Response: 
  Status: 401 Unauthorized
  {
    "detail": "Not authenticated"
  }
(FastAPI handles this automatically)


Request WITH token:
  GET /items/
  Authorization: Bearer my_token_here
  
Response:
  Status: 200 OK
  {
    "token": "my_token_here"
  }
"""


# ==============================================================================
# Step 4: Swagger automatically gets Authorize button
# ==============================================================================

"""
Visit: http://localhost:8000/docs

You see:
  - "Authorize" button at top
  - Lock icon on /items/ endpoint
  
When you click Authorize:
  - Form appears for username/password
  - Swagger sends to /token endpoint (doesn't exist yet)
  - Swagger saves the token
  - Swagger includes token in Authorization header for all requests

Note: Swagger is test tool, not real frontend
Real frontend does same: get token -> include in requests
"""


# ==============================================================================
# Step 5: Code example (complete minimal setup)
# ==============================================================================

"""
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    return {"token": token}

@app.get("/users/me")
async def read_user_me(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    return {"current_user_token": token}
"""

# ACTUAL WORKING CODE EXAMPLE

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Protected endpoint - requires token in Authorization header
    Try without token: 401 Unauthorized
    Try with token: Returns the token
    """
    return {"token": token}


@app.get("/users/me")
async def read_user_me(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Another protected endpoint
    """
    return {"current_user_token": token}


@app.get("/public")
async def public_endpoint():
    """
    Unprotected endpoint - anyone can access
    """
    return {"message": "This is public"}


# TESTING:
# 1. No token:
#    GET /items/
#    Response: 401 Unauthorized
#
# 2. With token:
#    GET /items/
#    Authorization: Bearer my-fake-token
#    Response: {"token": "my-fake-token"}
#
# 3. Public endpoint:
#    GET /public
#    Response: {"message": "This is public"}


# ==============================================================================
# What's NOT done yet (next steps)
# ==============================================================================

"""
Current code only:
  - Requires token to exist
  - Reads token from header
  - Returns 401 if missing

NOT done:
  - Check username/password
  - Generate real tokens
  - Validate token format
  - Check token expiration
  - Store user information in token

This is STEP 1 of security
Next: Implement /token endpoint, password hashing, token validation
"""
