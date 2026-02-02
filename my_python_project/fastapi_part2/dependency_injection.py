"""
DEPENDENCY INJECTION
====================
Basically: write a function to handle logic, then use it across multiple endpoints without copy-pasting.
"""

from fastapi import FastAPI, Depends
from typing import Annotated

app = FastAPI()


# 1. THE BASICS
# =============
# Imagine you have 2 endpoints that need the same job (get skip & limit)
# Instead of writing it twice, create 1 function and reuse it


def get_pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@app.get("/items/")
def read_items(params: Annotated[dict, Depends(get_pagination)]):
    # FastAPI will call get_pagination() and pass the result here
    return params


@app.get("/users/")
def read_users(params: Annotated[dict, Depends(get_pagination)]):
    # Same function, reused - no need to rewrite the logic
    return params


# 2. USE IT TO CHECK TOKEN/AUTH
# ==============================
def get_current_user(token: str = "abc123"):
    # This is a dependency - every request will run this function first
    if token != "abc123":
        raise Exception("Invalid token!")
    return {"username": "tuyen", "email": "tuyen@example.com"}


@app.get("/profile/")
def get_profile(user: Annotated[dict, Depends(get_current_user)]):
    # Only correct token can access this endpoint
    return user


# 3. DEPENDENCY DEPENDING ON ANOTHER DEPENDENCY
# ==============================================
def get_admin_user(user: Annotated[dict, Depends(get_current_user)]):
    # This will run get_current_user() first, then run this one
    # Flow: request -> get_current_user() -> get_admin_user() -> endpoint
    if user["username"] != "tuyen":
        raise Exception("Admin only!")
    return {**user, "is_admin": True}


@app.get("/admin/")
def admin_panel(user: Annotated[dict, Depends(get_admin_user)]):
    # Two-level authentication: pass get_current_user first, then admin check
    return user


# 4. EASIER WAY - TYPE ALIAS
# ===========================
# Instead of writing Annotated[dict, Depends(...)] all day, use an alias

AuthUser = Annotated[dict, Depends(get_current_user)]
PaginationParams = Annotated[dict, Depends(get_pagination)]


@app.get("/search/")
def search(user: AuthUser, params: PaginationParams):
    # Cleaner and easier to read
    return {"user": user, "params": params}


# 5. DEPENDS vs QUERY vs BODY - HOW ARE THEY DIFFERENT
# =====================================================
"""
Query:   GET /items/?skip=5
         -> Get from URL, simple parameters
         -> Not easy to reuse

Body:    POST /items/ + JSON
         -> Get from request body
         -> Validation follows schema

Depends: Run a function
         -> Function can check token, query DB, handle any logic
         -> Reuse across multiple endpoints at once
         -> Easiest to test

In short: Query & Body = get data from request
          Depends = run logic, share logic
"""


# 6. WHY Depends(function) AND NOT Depends(function())
# =====================================================
"""
Wrong:  Depends(get_pagination())
        -> You call the function immediately, FastAPI doesn't know it's a dependency
        -> Function runs once when code loads, not per request

Right:  Depends(get_pagination)
        -> You only pass the function to FastAPI, don't call it
        -> FastAPI will call it when a request comes
        -> Runs once per request

Example:
get_pagination()     <- "do it now!" -> runs when code loads
get_pagination      <- "i'll do it when needed" -> runs when request arrives
"""


# 7. WHAT ANNOTATED DOES
# =======================
"""
Annotated[dict, Depends(get_pagination)]
           ↑    ↑
         Type  How to get data

= "This parameter is dict, get value from function get_pagination"

With Annotated:
  - IDE understands params is dict -> suggests .keys(), .values(), etc
  - Type checker validates data type
  - Code documents itself

Without Annotated:
  - IDE doesn't know what params is
  - Autocomplete doesn't work
  - Hard to maintain

In short: Annotated helps IDE & type checker understand code better
"""


# 8. USE 1 DEPENDENCY IN MULTIPLE PLACES
# ======================================
"""
Benefits of dependency:

Example 1: Same dependency, 3 endpoints
  AuthUser = Annotated[dict, Depends(get_current_user)]
  
  @app.get("/profile/")
  def profile(user: AuthUser): ...
  
  @app.get("/settings/")  
  def settings(user: AuthUser): ...
  
  @app.delete("/account/")
  def delete(user: AuthUser): ...
  
  -> Want to change auth logic? Fix it once, all 3 endpoints update

Example 2: Dependency chain (dependency calls another dependency)
  get_admin(user: Depends(get_current_user))
  -> Can chain as many levels as you want

Example 3: One endpoint, multiple dependencies at once
  @app.get("/admin/data/")
  def admin_data(
      user: Annotated[dict, Depends(get_admin_user)],
      pagination: Annotated[dict, Depends(get_pagination)]
  ):
      # 2 dependencies run at the same time, results injected into endpoint

In short:
- Write once, use anywhere
- Fix once, all updates everywhere
- Easier to test
- No code repetition
"""
