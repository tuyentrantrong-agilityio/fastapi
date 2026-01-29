# Status Code - HTTP Status Codes
#
# Each API response has 2 parts:
#   1. Status code (number): 200, 201, 404, 500...
#   2. Body (JSON): {"name": "Book", ...}
#
# Example:
#   HTTP/1.1 200 OK
#   {"name": "Book"}
#
# Status code = tells client what happened
# Body = actual data


from fastapi import FastAPI, status
from http import HTTPStatus

app = FastAPI()


# DEFAULT STATUS CODE
# ===================
# If not specified, FastAPI defaults to 200 OK


@app.post("/items/")
async def create_item(name: str):
    # Client receives 200 OK
    # But HTTP standard recommends 201 Created for creating new resources
    return {"name": name}


# DECLARE STATUS CODE
# ===================
# Use status_code parameter in decorator


@app.post("/items/", status_code=201)
async def create_item_with_status(name: str):
    # Client receives 201 Created
    return {"name": name}


# IMPORTANT: status_code is in decorator, NOT in function parameter
# WRONG:
# async def create_item(status_code=201, name: str):

# CORRECT:
# @app.post("/items/", status_code=201)
# async def create_item(name: str):


# WAYS TO DECLARE STATUS CODE
# ============================


# Method 1: Using number (not recommended)
@app.post("/posts/", status_code=201)
async def create_post_v1(title: str):
    return {"title": title}


# Method 2: Using HTTPStatus from http module
@app.post("/posts/v2/", status_code=HTTPStatus.CREATED)
async def create_post_v2(title: str):
    return {"title": title}


# Method 3: Using fastapi.status (RECOMMENDED)
# Why? IDE auto-completion, readable, less mistakes
@app.post("/posts/v3/", status_code=status.HTTP_201_CREATED)
async def create_post_v3(title: str):
    return {"title": title}


# WHAT DOES FASTAPI DO WITH STATUS CODE?
# =======================================
# 1. Returns that status code to client
#    HTTP/1.1 201 Created
#
# 2. Writes it to OpenAPI/Swagger documentation
#    Client knows this API returns 201 on success


# COMMON STATUS CODES
# ===================


# 2xx: Success
# ============
# 200 OK - request succeeded, returns data
@app.get("/items/{item_id}", status_code=status.HTTP_200_OK)
async def get_item(item_id: int):
    return {"id": item_id, "name": "Item"}


# 201 Created - successfully created new resource
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item_201(name: str):
    return {"id": 1, "name": name}


# 202 Accepted - request accepted but not processed yet
@app.post("/tasks/", status_code=status.HTTP_202_ACCEPTED)
async def create_task(task: str):
    # Usually for async/background processing
    return {"status": "processing"}


# 204 No Content - success but no data returned
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    # Response has no body
    return None


# 4xx: Client Error (client sent wrong data)
# ============================================
# 400 Bad Request - invalid data
@app.post("/validate/", status_code=status.HTTP_400_BAD_REQUEST)
async def bad_request_example():
    # Use when validation fails
    return {"error": "Invalid data"}


# 401 Unauthorized - not logged in
# 403 Forbidden - no permission
# 404 Not Found - resource not found
@app.get("/users/{user_id}", status_code=status.HTTP_404_NOT_FOUND)
async def user_not_found(user_id: int):
    return {"error": "User not found"}


# 5xx: Server Error (backend error)
# ==================================
# 500 Internal Server Error - general error
# 503 Service Unavailable - server temporarily offline
#
# You rarely set these manually - FastAPI returns them on code error


# HTTP STATUS CODE CHEAT SHEET
# ============================
# 1xx - Information (rarely used, no body)
# 2xx - Success (200, 201, 202, 204)
# 3xx - Redirection (301, 302, 304...)
# 4xx - Client Error (400, 401, 403, 404, 409...)
# 5xx - Server Error (500, 503...)


# BEST PRACTICE
# =============
# 1. Always use fastapi.status (not numbers)
# 2. Choose correct status code per HTTP standard
# 3. Document status codes in docstring
# 4. Use exceptions for errors (not just status code)
