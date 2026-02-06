"""
OAUTH2 SCOPES - QUICK REFERENCE

Scope = Permission token (like access card)
- Token has scopes: ["me", "items"]
- API says: "need items scope"
- FastAPI checks & allows/denies access

Use Security() to check scopes (not Depends!)
"""

from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone

app = FastAPI()

scopes_description = {
    "me": "Read user profile",
    "items": "Read/write items",
    "admin": "Admin access",
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=scopes_description)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    scopes: list[str] = []


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Decode JWT token & extract scopes"""
    try:
        payload = jwt.decode(token, "secret-key", algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(username=username, scopes=payload.get("scopes", []))
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ===== EXAMPLES =====


@app.get("/status")
async def public():
    """No auth needed"""
    return {"status": "ok"}


@app.get("/users/me")
async def my_profile(
    user: Annotated[TokenData, Security(get_current_user, scopes=["me"])],
):
    """Requires "me" scope"""
    return {"username": user.username}


@app.get("/users/me/items")
async def my_items(
    user: Annotated[TokenData, Security(get_current_user, scopes=["me", "items"])],
):
    """Requires both "me" AND "items" scopes"""
    return {"items": ["item1", "item2"]}


@app.post("/users/me/items")
async def create_item(
    user: Annotated[
        TokenData, Security(get_current_user, scopes=["me", "items", "admin"])
    ],
    item_name: str,
):
    """Requires "me", "items", AND "admin" scopes"""
    return {"created": item_name}


@app.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Login: select scopes in Swagger, get token.
    Swagger UI shows checkboxes for all available scopes.
    """
    username = form_data.username
    scopes = (form_data.scopes or "").split()

    token = jwt.encode(
        {
            "sub": username,
            "scopes": scopes,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "secret-key",
        algorithm="HS256",
    )
    return Token(access_token=token, token_type="bearer")


"""
SUMMARY

Security() vs Depends():
  Depends()    → call function only
  Security()   → call function + check scopes + show in Swagger

Flow:
1. POST /token → select scopes → get token with scopes
2. GET /users/me (with token) → FastAPI checks if token has needed scopes
3. Match? → ✓ proceed / Mismatch? → ✗ 403

Example:
- Token has: ["me", "items"]
- GET /users/me needs ["me"] → ✓ OK
- POST /users/me/items needs ["me", "items", "admin"] → ✗ Missing "admin"

When to use:
✓ Permission-based APIs
✓ Role-based access control
"""
