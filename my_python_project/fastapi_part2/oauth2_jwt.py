"""
OAuth2 + JWT + Password Hashing - Concise Working Example

Key Ideas:
- Password: sent ONCE at login only
- JWT Token: signed, has expiration
- Hash: password stored as irreversible hash (bcrypt)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext

# ============ CONFIG ============
SECRET_KEY = "change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============ PASSWORD HASHING ============
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ============ MODELS ============
class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False


class UserInDB(User):
    hashed_password: str


# ============ DATABASE ============
fake_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "john@example.com",
        "hashed_password": get_password_hash("secret"),
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "hashed_password": get_password_hash("pass123"),
        "disabled": True,
    },
}

# ============ SETUP ============
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ============ JWT FUNCTIONS ============
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """Decode JWT and return username"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


# ============ HELPERS ============
def get_user_db(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    if username in fake_db:
        return UserInDB(**fake_db[username])
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Verify username + password"""
    user = get_user_db(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ============ DEPENDENCIES ============
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract user from token"""
    username = decode_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_db(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check user is active"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="User disabled")
    return current_user


# ============ ENDPOINTS ============
@app.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login: exchange username/password for JWT token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get current user (requires valid token)"""
    return current_user


@app.get("/users/me/items")
async def read_my_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Another protected endpoint"""
    return [
        {"item": "Foo", "owner": current_user.username},
        {"item": "Bar", "owner": current_user.username},
    ]


# ============ FLOW EXPLANATION ============
"""
LOGIN FLOW (Password sent once):
1. POST /token with username=johndoe&password=secret
2. Server finds user, hashes password, compares with stored hash
3. If match: create JWT {"sub": "johndoe", "exp": ...}
4. Sign JWT with SECRET_KEY
5. Return {"access_token": "eyJ...", "token_type": "bearer"}

SUBSEQUENT REQUESTS (No password):
1. GET /users/me with Authorization: Bearer eyJ...
2. oauth2_scheme extracts token from header
3. decode_access_token verifies signature + expiration
4. Extract username from token
5. get_current_user loads user from database
6. get_current_active_user checks user not disabled
7. Endpoint executed

SECURITY:
- Password sent once (login only)
- Password hashed (bcrypt - irreversible)
- Token has expiration (30 min default)
- Token is signed (can't forge)
- Requests don't need password

TEST WITH curl:

# 1. Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=secret"

# Returns: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Use token (replace TOKEN_HERE)
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer TOKEN_HERE"

# Returns: {"username": "johndoe", "email": "john@example.com", ...}
"""
