"""
OAuth2 Password Bearer - Simple Examples with English Explanations

Core Concept: OAuth2 is just login + token system
1. User logs in with username/password → gets a token (like an ID card)
2. User uses token for other API calls → no need to send password again
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional

# ============================================================================
# STEP 1: Setup Models
# ============================================================================


class User(BaseModel):
    """Represents a user in the system"""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """User stored in database with hashed password"""

    hashed_password: str


# ============================================================================
# STEP 2: Create Fake Database & Setup
# ============================================================================

# Fake user database (in real app: use actual database)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    }
}

app = FastAPI()

# OAuth2PasswordBearer: Extract token from Authorization header
# tokenUrl="token" → tells Swagger where to authenticate
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ============================================================================
# STEP 3: Helper Functions
# ============================================================================


def fake_hash_password(password: str) -> str:
    """
    Simulate hashing a password (never store plain passwords!)
    In production: use bcrypt or argon2
    """
    return "fakehashed" + password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password matches hashed version
    In production: use bcrypt.verify()
    """
    return fake_hash_password(plain_password) == hashed_password


def get_user(db: dict, username: str) -> Optional[UserInDB]:
    """Get user from database by username"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


# ============================================================================
# STEP 4: Authentication Endpoints
# ============================================================================


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - user provides username/password, gets token

    OAuth2PasswordRequestForm automatically handles form-data parsing
    (username, password fields from form submission)

    Returns: token for use in subsequent API calls
    """

    # Step 4a: Find user in database
    user = get_user(fake_users_db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 4b: Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 4c: Return token (in real app: use JWT)
    return {"access_token": user.username, "token_type": "bearer"}


# ============================================================================
# STEP 5: Get Current User (Dependency)
# ============================================================================


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Extract token from header and get user

    - oauth2_scheme reads Authorization header
    - Returns user if token is valid
    - Raises 401 if no token or token invalid
    """

    # Get user using token (in real app: decode JWT)
    user = get_user(fake_users_db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify user account is not disabled

    This is a chained dependency:
    token → current_user → active user
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ============================================================================
# STEP 6: Protected Endpoints
# ============================================================================


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current logged-in user

    - Requires: valid token + active user
    - Depends(get_current_active_user) blocks request if:
      - No token → 401 Unauthorized
      - Invalid token → 401 Unauthorized
      - User disabled → 400 Bad Request
    """
    return current_user


@app.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    """
    Another protected endpoint - reuse same dependency
    """
    return [{"item_name": "Foo", "owner": current_user.username}]


# ============================================================================
# QUICK FLOW SUMMARY
# ============================================================================
"""
1. User sends: POST /token with username/password
   ↓
2. Server verifies: password correct?
   ↓
3. Server returns: {"access_token": "johndoe", "token_type": "bearer"}
   ↓
4. User sends: GET /users/me with Authorization: Bearer johndoe
   ↓
5. oauth2_scheme extracts token from header
   ↓
6. get_current_user retrieves user from database
   ↓
7. get_current_active_user checks user not disabled
   ↓
8. Endpoint executed → returns user data

Why this design?
- Never send password in multiple requests (security)
- Token can expire (adds time limit)
- Easy to revoke tokens (logout)
- Token can encode user info (JWT)
"""
