# Form Data - Send data via HTML Form
#
# Client can send data to server in 2 main ways:
#   1. JSON (from app/Postman): {"name": "Huy", "age": 20}
#   2. Form Data (from HTML form): username=tuyen&password=123456
#
# FastAPI needs to know which type → use Form() to specify


from fastapi import FastAPI, Form
from typing import Annotated

app = FastAPI()


# PROBLEM: FastAPI defaults to expecting JSON
# ===========================================
# If client sends form data without Form()
# → FastAPI thinks it's JSON → 422 Unprocessable Entity


# ❌ WRONG: No Form() declaration
@app.post("/login-wrong/")
async def login_wrong(username: str, password: str):
    # Client sends form data
    # FastAPI expects JSON
    # → Error 422!
    return {"username": username}


# ✅ CORRECT: Use Form() to receive form data
@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    # Form() = "this time client sends form data, not JSON"
    # FastAPI will parse form data into username, password
    return {"username": username}


# How does HTML Form send data?
# ==============================
# <form action="/login" method="post">
#   <input name="username" placeholder="Enter username">
#   <input type="password" name="password" placeholder="Enter password">
#   <button type="submit">Login</button>
# </form>
#
# When submit button pressed:
#   Browser sends: application/x-www-form-urlencoded
#   Data: username=tuyen&password=123456


# REAL EXAMPLES
# =============


# Endpoint that receives HTML form data
@app.post("/signup/")
async def signup(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
):
    """
    HTML form:
    <form action="/signup" method="post">
      <input name="email">
      <input name="password" type="password">
      <input name="full_name">
      <button>Sign up</button>
    </form>
    """
    return {"email": email, "password": password, "full_name": full_name}


# FORM vs JSON - When to use which?
# =================================
# JSON:
#   - From app/mobile app/Postman
#   - Use Body() or default
#   - Flexible, structured
#
# Form:
#   - From HTML form (browser)
#   - Must use Form()
#   - Simple, traditional


# EXAMPLE: JSON vs Form
# ====================

# Endpoint 1: Receive JSON (from app/Postman)
from pydantic import BaseModel


class UserIn(BaseModel):
    email: str
    password: str
    full_name: str


@app.post("/api/signup/")
async def api_signup(user: UserIn):
    # POST JSON:
    # {"email": "...", "password": "...", "full_name": "..."}
    return user


# Endpoint 2: Receive Form Data (from HTML form)
@app.post("/web/signup/")
async def web_signup(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
):
    # POST Form Data:
    # email=...&password=...&full_name=...
    return {"email": email, "password": password, "full_name": full_name}


# WHY OAUTH2 REQUIRES FORM?
# ==========================
# OAuth2 is an old standard (predates JSON popularity)
# It requires: username + password MUST be sent as form-data
#
# FastAPI can't break OAuth2 standard
# So must use Form() for OAuth2 endpoints


# FASTAPI PRINCIPLES
# ==================
# Body (JSON):     you specify Body()
# Query param:     you specify Query() (or default)
# Form data:       you specify Form()
# File upload:     you specify File()
#
# If not specified → FastAPI defaults to Body/Query


# NOTE
# ====
# To use Form(), need: pip install python-multipart
# FastAPI automatically uses it to parse form data
