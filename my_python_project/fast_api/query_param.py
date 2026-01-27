"""
FastAPI Query Parameters Tutorial
===================================
Learn how to use query parameters to pass optional or required data in URLs.
Query parameters are key-value pairs that appear after the ? in a URL.
"""

from fastapi import FastAPI
from typing import Optional

app = FastAPI()


# ============================================================================
# 1. WHAT ARE QUERY PARAMETERS?
# ============================================================================

"""
Query parameters are variables that come AFTER the ? in a URL.

Format: ?key=value&key=value

Example:
    URL: /items/?skip=0&limit=10
    
    Query parameters:
    - skip = 0
    - limit = 10

Difference from Path Parameters:
┌─────────────────────────────────────────────────────────┐
│ PATH: /users/{user_id}                                  │
│   - {user_id} goes in the URL path                       │
│   - Identifies the resource                             │
│                                                           │
│ QUERY: /items/?skip=0&limit=10                         │
│   - skip, limit come after ?                            │
│   - Used for filtering, pagination, options            │
└─────────────────────────────────────────────────────────┘
"""


# ============================================================================
# 2. BASIC QUERY PARAMETERS WITH DEFAULT VALUES
# ============================================================================

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    """
    Basic query parameters with default values.
    
    How FastAPI knows these are query parameters:
    ✓ No {brackets} in the path → query parameter
    ✓ Parameters have default values → optional
    
    Example calls:
    ✅ /items/                  → skip=0, limit=10 (defaults)
    ✅ /items/?skip=5           → skip=5, limit=10
    ✅ /items/?limit=20         → skip=0, limit=20
    ✅ /items/?skip=5&limit=20  → skip=5, limit=20
    """
    return {"skip": skip, "limit": limit}


# ============================================================================
# 3. TYPE HINTS = AUTOMATIC BENEFITS
# ============================================================================

"""
Type hints unlock FastAPI's "magic":

skip: int
limit: int

FastAPI automatically:
┌──────────────────────────────────────────────────┐
│ 1. PARSE - Convert URL string to Python int     │
│    URL: /items/?skip=5 → skip = 5 (int type)    │
│                                                   │
│ 2. VALIDATE - Check data is valid               │
│    URL: /items/?skip=abc → Error (not an int)   │
│                                                   │
│ 3. DOCUMENT - Generate interactive docs         │
│    Visit: http://127.0.0.1:8000/docs            │
│                                                   │
│ 4. ERROR MESSAGES - Show helpful errors         │
│    Response: "Input should be a valid integer"  │
└──────────────────────────────────────────────────┘

Same behavior as path parameters!
"""


# ============================================================================
# 4. OPTIONAL QUERY PARAMETERS (None as default)
# ============================================================================

@app.get("/items/{item_id}")
async def read_item_optional(
    item_id: str,
    q: Optional[str] = None,
):
    """
    Optional query parameter using None.
    
    Meaning:
    - q may or may not be provided
    - If not provided, q defaults to None
    - q: Optional[str] = None  OR  q: str | None = None (Python 3.10+)
    
    Example calls:
    ✅ /items/abc             → item_id="abc", q=None
    ✅ /items/abc?q=123       → item_id="abc", q="123"
    ✅ /items/abc?q=hello     → item_id="abc", q="hello"
    ❌ /items/?q=test         → Error (item_id required, it's a path param)
    """
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


# ============================================================================
# 5. BOOLEAN QUERY PARAMETERS
# ============================================================================

@app.get("/items_bool/{item_id}")
async def read_item_bool(
    item_id: str,
    short: bool = False,
):
    """
    Boolean query parameters.
    
    FastAPI accepts these as True:
    ✅ ?short=1
    ✅ ?short=true
    ✅ ?short=True
    ✅ ?short=yes
    ✅ ?short=on
    
    And this as False:
    ✅ ?short=0        → False
    ✅ ?short=false    → False
    ✅ (not provided)   → False (default)
    
    Example calls:
    ✅ /items_bool/abc           → short=False
    ✅ /items_bool/abc?short=1   → short=True
    ✅ /items_bool/abc?short=yes → short=True
    """
    return {"item_id": item_id, "short": short}


# ============================================================================
# 6. COMBINING PATH AND QUERY PARAMETERS
# ============================================================================

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,
    item_id: str,
    q: Optional[str] = None,
    short: bool = False,
):
    """
    Combining both path and query parameters.
    
    FastAPI automatically detects:
    - {user_id}, {item_id} → PATH parameters (in URL path)
    - q, short → QUERY parameters (after ?)
    
    Example URL: /users/1/items/abc?q=123&short=true
    
    FastAPI understands:
    ✓ user_id = 1 (path parameter, converted to int)
    ✓ item_id = "abc" (path parameter)
    ✓ q = "123" (query parameter)
    ✓ short = True (query parameter, converted to bool)
    """
    return {
        "user_id": user_id,
        "item_id": item_id,
        "q": q,
        "short": short,
    }


# ============================================================================
# 7. REQUIRED QUERY PARAMETERS (No default)
# ============================================================================

@app.get("/items_required/")
async def read_item_required(
    needy: str,
):
    """
    Required query parameter (no default value).
    
    Meaning:
    - needy MUST be provided
    - If missing, FastAPI returns error: "Field required"
    
    Example calls:
    ❌ /items_required/            → Error (missing needy)
    ✅ /items_required/?needy=abc  → needy="abc"
    ✅ /items_required/?needy=123  → needy="123"
    """
    return {"needy": needy}


# ============================================================================
# 8. COMBINING ALL QUERY PARAMETER TYPES
# ============================================================================

@app.get("/items_complete/{item_id}")
async def read_item_complete(
    item_id: str,           # PATH parameter (required by URL path)
    needy: str,             # QUERY parameter (required, no default)
    skip: int = 0,          # QUERY parameter (optional, has default)
    limit: Optional[int] = None,  # QUERY parameter (optional, can be None)
):
    """
    Complete example using all query parameter types.
    
    Parameter types breakdown:
    ┌──────────────────────────────────────────────────────┐
    │ item_id: str                                         │
    │   - Path parameter, always required                  │
    │                                                      │
    │ needy: str                                           │
    │   - Query parameter, required (no default value)     │
    │   - Must include in URL: ?needy=value                │
    │                                                      │
    │ skip: int = 0                                        │
    │   - Query parameter, optional with default           │
    │   - If not provided, uses 0                          │
    │                                                      │
    │ limit: Optional[int] = None                          │
    │   - Query parameter, optional, can be None           │
    │   - If not provided, uses None                       │
    └──────────────────────────────────────────────────────┘
    
    Example calls:
    ❌ /items_complete/abc                    → Error (needy required)
    ✅ /items_complete/abc?needy=test         → Complete!
    ✅ /items_complete/abc?needy=x&skip=5     → Complete!
    ✅ /items_complete/abc?needy=x&limit=100  → Complete!
    ✅ /items_complete/abc?needy=x&skip=5&limit=100 → All provided!
    """
    return {
        "item_id": item_id,
        "needy": needy,
        "skip": skip,
        "limit": limit,
    }


# ============================================================================
# 9. QUERY PARAMETER PATTERNS SUMMARY
# ============================================================================

"""
Quick Reference: When to Use Each Pattern

┌────────────────────────────────────────────────────────────┐
│ REQUIRED with default (unusual)                           │
│   param: type = value                                      │
│   - Always required in URL                                │
│   - Default only if function called directly              │
│                                                             │
│ OPTIONAL with default (common)                            │
│   param: type = value                                      │
│   - Provided in URL? Use URL value                         │
│   - Not provided? Use default value                        │
│                                                             │
│ OPTIONAL, can be None (flexible)                          │
│   param: Optional[type] = None  OR  param: type | None   │
│   - Provided in URL? Use it                               │
│   - Not provided? Set to None                             │
│                                                             │
│ REQUIRED, no default (strict)                             │
│   param: type                                              │
│   - MUST be in URL or FastAPI returns error              │
│   - Use for critical filters                              │
└────────────────────────────────────────────────────────────┘
"""
