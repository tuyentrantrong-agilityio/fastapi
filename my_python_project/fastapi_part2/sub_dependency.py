"""
SUB-DEPENDENCIES - Dependency depends on another dependency

Basic concepts:
- Dependency: function automatically handles request data
- Sub-dependency: dependency calls another dependency to get data

Real-world example:
  Online cake order - Service staff needs to check inventory first
  Service staff is dependency, inventory check is sub-dependency
"""

from typing import Annotated
from fastapi import FastAPI, Cookie, Depends

# ==============================================================================
# Example 1: Basic sub-dependency
# ==============================================================================


# FUNCTION 1: query_extractor (SUB-DEPENDENCY)
# Get query parameter ?q=... from URL
def query_extractor(q: str | None = None):
    """Extract query value from URL. Example: /items/?q=hello -> q='hello'"""
    return q


# FUNCTION 2: query_or_cookie_extractor (MAIN DEPENDENCY)
# Get data from query or cookie, must call query_extractor first


def query_or_cookie_extractor(
    q: Annotated[str | None, Depends(query_extractor)] = None,
    last_query: Annotated[str | None, Cookie()] = None,
):
    """
    Get from query if exists, otherwise get from cookie.
    Important line: Depends(query_extractor)
    It says: get result from query_extractor, don't get directly
    """
    if not q:
        return last_query
    return q


# ==============================================================================
# Example 2: Route using sub-dependency
# ==============================================================================

app = FastAPI()


@app.get("/items/")
async def read_query(
    query_or_detail: Annotated[str | None, Depends(query_or_cookie_extractor)] = None,
):
    """
    This route tells FastAPI: "Before running this function, call query_or_cookie_extractor"
    FastAPI automatically runs in order:

    Request /items/ -> query_extractor() -> query_or_cookie_extractor() -> read_query()

    You don't need to:
    - Call manually
    - Pass parameters
    - Care about order
    """
    return {"q_or_cookie": query_or_detail}


# ==============================================================================
# Explanation: Where is sub-dependency?
# ==============================================================================

"""
query_extractor is SUB-DEPENDENCY because:
  1. It's used inside query_or_cookie_extractor (another dependency)
  2. It's not used directly for the route
  3. Only called when route needs query_or_cookie_extractor

Comparison:
  - query_extractor: SUB-dependency (helper)
  - query_or_cookie_extractor: MAIN DEPENDENCY
  - read_query: ROUTE
"""


# ==============================================================================
# Optimization: Does FastAPI call it only once?
# ==============================================================================

"""
If 2 dependencies both use query_extractor, how many times does FastAPI call it?

Answer: Only once!
FastAPI is smart:
  - First time: Call query_extractor, save result
  - Next time: Use old result, don't call again

Example:
  dependency_1(q=Depends(query_extractor))
  dependency_2(q=Depends(query_extractor))
  
  -> query_extractor() called once, both use that result

Benefit: Efficient, no duplicate runs
"""


# ==============================================================================
# Advanced: When to use use_cache=False?
# ==============================================================================

"""
use_cache=False: Force FastAPI to call dependency again each time, don't save result

When needed? 
  - Dependency has side-effect (example: log, count request)
  - Need fresh data each time

Example:
  Depends(query_extractor, use_cache=False)
  
But: Usually not needed, only use when you have clear reason
"""
