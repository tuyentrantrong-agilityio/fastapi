"""FastAPI Cookies - Receive data from browser cookies"""

from fastapi import FastAPI, Cookie
from typing import Annotated

app = FastAPI()


# ============================================================================
# 1. WHAT IS A COOKIE?
# ============================================================================
# Cookie = small data that browser stores locally
# Browser automatically sends it with each request
# Used for: login, tracking, preferences
# Server reads cookie using Cookie()


# ============================================================================
# 2. BASIC SYNTAX
# ============================================================================


@app.get("/items/")
def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    # Syntax: Annotated[type, Cookie()]
    # ads_id = cookie name
    # str | None = cookie may or may not exist
    # Cookie() = tells FastAPI: this is a cookie, not a query param
    # = None = if browser doesn't send → receive None
    return {"ads_id": ads_id}


# ============================================================================
# 3. REQUIRED COOKIE
# ============================================================================


@app.get("/profile/")
def get_profile(session_id: Annotated[str, Cookie()]):
    # No = None → cookie is required
    # If browser doesn't send session_id → error 422
    return {"session": session_id}


# ============================================================================
# 4. COOKIE WITH VALIDATION
# ============================================================================


@app.get("/dashboard/")
def dashboard(
    user_id: Annotated[int | None, Cookie(description="User ID from cookie")] = None,
):
    # Add description like Query/Path
    # FastAPI auto converts str → int
    # Swagger docs will display description
    return {"user": user_id}


# ============================================================================
# 5. MULTIPLE COOKIES
# ============================================================================


@app.get("/secure/")
def secure_endpoint(
    session: Annotated[str | None, Cookie()] = None,
    theme: Annotated[str | None, Cookie()] = None,
    language: Annotated[str | None, Cookie()] = None,
):
    # Browser can send multiple cookies
    # FastAPI auto extracts from request
    return {"session": session, "theme": theme, "language": language}


# ============================================================================
# 6. COOKIE VS QUERY
# ============================================================================
# WITHOUT Cookie():
#   def get_items(ads_id: str = None):
#   → FastAPI understands: /items/?ads_id=123 (QUERY)
#
# WITH Cookie():
#   def get_items(ads_id: Annotated[str, Cookie()]):
#   → FastAPI understands: cookie header (COOKIE)


# ============================================================================
# 7. ⚠️ IMPORTANT: TESTING COOKIES IN SWAGGER
# ============================================================================
# Swagger UI runs with JavaScript
# JavaScript cannot send arbitrary cookies
# → Even if you enter cookies in Swagger /docs, FastAPI will receive = None
#
# Correct way to test cookies:
# ✅ Real browser (DevTools)
# ✅ Postman
# ✅ Real frontend
# ❌ Swagger UI (doesn't work)


# ============================================================================
# 8. REAL-WORLD USAGE
# ============================================================================


@app.post("/login/")
def login(username: str, password: str):
    # When login, server creates session cookie
    # This response will set-cookie (browser saves automatically)
    #
    # from fastapi.responses import JSONResponse
    # response = JSONResponse({"message": "login ok"})
    # response.set_cookie(key="session_id", value="abc123")
    # return response

    return {"message": "logged in"}


@app.get("/me/")
def get_current_user(session_id: Annotated[str | None, Cookie()] = None):
    # Next step: browser sends cookie session_id
    # FastAPI reads, checks who is logged in
    if not session_id:
        return {"error": "not logged in"}
    return {"user": "john", "session": session_id}


# ============================================================================
# SUMMARY
# ============================================================================
# 1. Cookie = Annotated[type, Cookie()]
# 2. Same as Query/Path, same syntax, different location
# 3. Browser sends cookie, FastAPI reads it
# 4. Test with browser/Postman, NOT Swagger
# 5. Use for login, session, preference
