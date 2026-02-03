"""
DEPENDENCY IN DECORATOR - Run dependency without getting return value

Problem:
Usually dependency must be declared in parameter and get the return value.
But sometimes you only need dependency to run (check, log), not use the result.

Specific problem:
  async def read_items(token: str = Depends(verify_token)):  # token not used!
      return items

IDE reports: "unused parameter" - Confusing!

Solution:
  Put dependency in decorator (not in parameter)
  - Dependency runs, but does not pass result to function

Real-world example:
  Movie theater ticket control:
    - Guard checks ticket (dependency)
    - You can enter, don't need to keep ticket
    - Guard doesn't give ticket back
"""

from typing import Annotated
from fastapi import FastAPI, Header, HTTPException, Depends

app = FastAPI()

# ==============================================================================
# Example 1: Dependency checking token
# ==============================================================================


async def verify_token(x_token: Annotated[str, Header()]):
    """
    Check x-token header.
    - Wrong: raise error (block request)
    - Correct: allow (even with no return)
    """
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="Invalid token")


# ==============================================================================
# Example 2: Dependency checking API key
# ==============================================================================


async def verify_key(x_key: Annotated[str, Header()]):
    """
    Check x-key header.
    Has return but decorator dependency ignores return.
    Whether returns or not doesn't matter, just needs to run for checking.
    """
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="Invalid key")
    return x_key  # Has return but decorator dependency will ignore it


# ==============================================================================
# Example 3: Endpoint using dependency in decorator
# ==============================================================================


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    """
    Dependencies in decorator:

    Flow:
      1. Request /items/
      2. FastAPI runs verify_token()
      3. FastAPI runs verify_key()
      4. If error: stop, return error
      5. If ok: run read_items()

    Note:
    - verify_token, verify_key must run
    - But does not pass result to function
    - Function doesn't need to declare token or key variables
    """
    return [{"items": "Foo"}, {"items": "Bar"}]


# ==============================================================================
# Comparison: Decorator vs Parameter
# ==============================================================================

"""
Property                           Decorator      Parameter
------------------------------------------------------------
Dependency runs?                   Yes            Yes
Get value to use in function?      No             Yes
Clean code, no extra variables?    Yes            No
IDE reports unused parameter?      No             Yes*
Code meaning is clear?             Yes            No

* If parameter is not used

EASY RULE:
  - NEED value -> Put in function parameter
  - ONLY need to run -> Put in decorator
"""


# ==============================================================================
# Example comparison: Wrong way vs Correct way
# ==============================================================================

# WRONG WAY: Dependency in parameter but not used
# async def read_items_wrong(token: str = Depends(verify_token)):
#     return [{"items": "Foo"}]
#     # IDE reports: unused parameter 'token'
#     # Others: "what is token used for?"


# CORRECT WAY: Dependency in decorator
# @app.get("/items/", dependencies=[Depends(verify_token)])
# async def read_items_correct():
#     return [{"items": "Foo"}]
#     # Clean, meaning is clear


# ==============================================================================
# When to use?
# ==============================================================================

"""
Decorator dependencies are great for:
  - Authentication: check if user is valid
  - Authorization: check if user has permissions
  - Rate limit: check if exceeds request limit
  - Logging: log the request
  - Audit: check/record activities
  - Validate header/IP: check header or IP is valid

Remember:
  Decorator dependency = Mini middleware for endpoint
  Simplest way to protect endpoint without messy code!
"""
