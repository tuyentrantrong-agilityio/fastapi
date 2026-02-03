"""
GLOBAL DEPENDENCY - Common rules for entire application

Concept:
  Global dependency is code that runs before EVERY endpoint to check/block requests.
  Any API call must pass through global dependency first.

Real-world example:
  Company - security gate:
    - All employees entering company must pass through security gate
    - Gate checks ID card, fingerprint
    - Invalid → blocked
    - Valid → can enter department

  Mapping:
    - Security gate = global dependency
    - Departments = /items, /users endpoints
"""

from typing import Annotated
from fastapi import FastAPI, Header, HTTPException, Depends

# ==============================================================================
# Step 1: Define dependencies for checking
# ==============================================================================


async def verify_token(x_token: Annotated[str, Header()]):
    """Check token from X-Token header"""
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="Invalid token")


async def verify_key(x_key: Annotated[str, Header()]):
    """Check key from X-Key header"""
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="Invalid key")


# ==============================================================================
# Step 2: Create FastAPI app with global dependencies
# ==============================================================================

app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])

"""
Line above means:
  FastAPI app has 2 global security gates
  Every request to any API must pass through:
    1. verify_token()
    2. verify_key()
"""


# ==============================================================================
# Step 3: Regular endpoints (no need to care about dependencies)
# ==============================================================================


@app.get("/items/")
async def read_items():
    """
    This endpoint:
    - Does not need to declare dependencies
    - Does not know what token/key is
    - Does not know how checks are done
    - Only runs after passing both security gates
    """
    return [{"items": "Foo"}, {"items": "Bar"}]


@app.get("/users/")
async def read_users():
    """
    Another endpoint, also protected by global dependency.
    Automatic, no extra code needed.
    """
    return [{"user": "John"}, {"user": "Jane"}]


# ==============================================================================
# Example Request: Correct vs Wrong
# ==============================================================================

"""
WRONG REQUEST 1: No header
  GET /items
  (no header)
  
  Result: 
    Blocked at security gate
    Endpoint does not run
    Response: 400 Invalid token


WRONG REQUEST 2: Invalid token
  GET /items
  X-Token: wrong-token
  X-Key: fake-super-secret-key
  
  Result:
    Blocked at verify_token
    Endpoint does not run
    Response: 400 Invalid token


CORRECT REQUEST: All valid headers
  GET /items
  X-Token: fake-super-secret-token
  X-Key: fake-super-secret-key
  
  Result:
    Passes both security gates
    Endpoint runs
    Response: [{"items": "Foo"}, {"items": "Bar"}]
"""


# ==============================================================================
# Comparison: Global vs Decorator vs Parameter Dependencies
# ==============================================================================

"""
Type                        Scope               When to use
------------------------------------------------------------------------
Global dependency           All endpoints       Check app-wide
                                                (auth, rate limit)

Decorator dependency        Single endpoint     Check this endpoint only
                            (dependencies=[...])

Parameter dependency        Single endpoint     Need value to use
                            (param: Type =      in endpoint
                            Depends(...))

RULE:
  - All endpoints -> Global dependency
  - Single endpoint -> Decorator dependency
  - Need value -> Parameter dependency
"""


# ==============================================================================
# Benefits of Global Dependency
# ==============================================================================

"""
1. Save code
   No need to write dependencies=[...] for each endpoint

2. Clean code
   Endpoints only focus on business logic

3. Easy to maintain
   Change one place, affects all endpoints

4. Consistency
   All endpoints follow same rule

Use cases:
  - Authentication (check user is valid)
  - Authorization (check user permissions)
  - Rate limiting (limit request count)
  - Logging (log all requests)
  - CORS checking
"""
