"""
FastAPI Path Parameters Tutorial
==================================
Learn how to use path parameters to build dynamic API endpoints.
Path parameters are variables defined within the URL.
"""

from fastapi import FastAPI
from enum import Enum

app = FastAPI()


# ============================================================================
# 1. BASIC ROOT ENDPOINT
# ============================================================================


@app.get("/")
def root():
    """Root endpoint returns a welcome message."""
    return {"hello": "world"}


# ============================================================================
# 2. PATH PARAMETERS - PURPOSE AND BENEFITS
# ============================================================================

# ❌ NO TYPE HINT - Not safe:
# @app.get("/items/{item_id}")
# async def read_item(item_id):
#     return {"item_id": item_id}  # item_id is string!


# ✅ WITH TYPE HINT - Safe and automatic:
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    Get item information by ID.

    Benefits of type hint (item_id: int):
    ┌─────────────────────────────────────────────────┐
    │ 1. AUTOMATIC TYPE CONVERSION                    │
    │    - URL: /items/3                              │
    │    - Python: item_id = 3 (int, not str)        │
    │                                                   │
    │ 2. AUTOMATIC VALIDATION                         │
    │    - URL: /items/foo                            │
    │    - Response: {"msg": "not a valid integer"}  │
    │    - No need to write if/try/except             │
    │                                                   │
    │ 3. AUTOMATIC DOCUMENTATION                      │
    │    - Access: http://127.0.0.1:8000/docs        │
    │    - FastAPI creates docs automatically         │
    └─────────────────────────────────────────────────┘
    """
    return {"item_id": item_id}


# ============================================================================
# 3. PATH PARAMETER ORDER IS VERY IMPORTANT ⚠️
# ============================================================================

# ⚠️ WRONG - Specific endpoint must come BEFORE endpoint with variable:
# @app.get("/users/{user_id}")  # ❌ Placed after
# async def read_user(user_id: str):
#     return {"user_id": user_id}
#
# @app.get("/users/me")  # ❌ Placed before (but FastAPI will treat /me as user_id)
# async def read_me():
#     return {"user_id": "current user"}
#
# When calling /users/me → FastAPI interprets user_id = "me" ❌ WRONG LOGIC


# ✅ CORRECT - Specific endpoint comes FIRST:
@app.get("/users/me")
async def read_me():
    """Get current user information."""
    return {"user_id": "current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    """Get user information by ID."""
    return {"user_id": user_id}


# 📌 RULE:
# - Endpoint with SPECIFIC path → place first (e.g., /users/me)
# - Endpoint with VARIABLE path → place after  (e.g., /users/{user_id})


# ============================================================================
# 4. ENUM - RESTRICT PARAMETER VALUES
# ============================================================================


class PetStatus(str, Enum):
    """Valid pet status values."""

    alive = "alive"
    dead = "dead"
    unknown = "unknown"


@app.get("/pets/{pet_status}")
async def read_pet(pet_status: PetStatus):
    """
    Find pet by status (only 3 values allowed).

    Example calls:
    ✅ /pets/alive   → OK
    ✅ /pets/dead    → OK
    ❌ /pets/alivee  → Error (invalid)

    Working with Enum:
    - Compare: if pet_status is PetStatus.alive:
    - Get value: PetStatus.alive.value
    - FastAPI returns: {"pet_status": "alive"}
    """
    return {"pet_status": pet_status}


# ============================================================================
# 5. PATH PARAMETER WITH SLASHES (Path with slashes)
# ============================================================================


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    """
    Get file by full path (including slashes).

    Syntax: {file_path:path}
    - `:path` allows parameter to contain /

    Example calls:
    ✅ /files/home/user/a.txt → file_path = "home/user/a.txt"
    ✅ /files/downloads/doc.pdf → file_path = "downloads/doc.pdf"

    Without :path:
    ❌ /files/home/user/a.txt → FastAPI misinterprets (thinks nested path)
    """
    return {"file_path": file_path}
