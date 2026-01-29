# Response Model - Data schema for API response
#
# Functions:
# 1. Validate response data matches schema
# 2. Auto-filter/remove sensitive fields
# 3. Auto-generate Swagger documentation

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None


# Method 1: Using return type annotation
# FastAPI will automatically treat it as response model
@app.post("/items/")
async def create_item(item: Item) -> Item:
    return item


# Method 2: Using response_model parameter (more explicit)
@app.post("/items/v2/", response_model=Item)
async def create_item_v2(item: Item):
    return item


# REAL EXAMPLE: Filter sensitive data
# =====================================
# This is the most important use case of response_model


class User(BaseModel):
    id: int
    username: str
    email: str
    password: str  # MUST NOT return to client!
    full_name: str
    is_admin: bool  # Sensitive information


class UserPublic(BaseModel):
    # Only return allowed fields
    id: int
    username: str
    full_name: str


# Test data
fake_users_db = [
    {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "password": "secret123",
        "full_name": "John Doe",
        "is_admin": True,
    }
]


# WRONG: No response_model
# Returns all data including password, email
@app.get("/users-wrong/{user_id}")
async def get_user_wrong(user_id: int):
    return fake_users_db[0]  # BUG: Returns password to client!


# CORRECT: Use response_model to filter
# FastAPI automatically removes fields not in UserPublic
@app.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: int):
    # Returns: id, username, full_name
    # Removes: password, email, is_admin
    return fake_users_db[0]


# VALIDATE RESPONSE DATA
# ======================
# Response must match schema, missing field → 500 error


class Product(BaseModel):
    id: int
    name: str
    price: float


@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    # If response missing 'price' → 500 error
    # {'id': 1, 'name': 'Laptop', 'price': 999.99} ✓
    # {'id': 1, 'name': 'Laptop'} ✗
    return {"id": 1, "name": "Laptop", "price": 999.99}


@app.get("/docs")
# /docs - Swagger automatically knows response schema from response_model


# ADVANCED FEATURES
# ==================

# 1. Response is list
@app.get("/items/", response_model=list[Item])
async def get_items():
    return [
        {"id": 1, "name": "Item 1", "price": 100},
        {"id": 2, "name": "Item 2", "price": 200},
    ]


# 2. Multiple response types (Union)
from typing import Union


class Error(BaseModel):
    error: str
    code: int


@app.get("/items-union/{item_id}", response_model=Union[Item, Error])
async def get_item_union(item_id: int):
    if item_id == 999:
        return {"error": "Not found", "code": 404}
    return {"id": 1, "name": "Item", "price": 100}


# RETURN TYPE vs RESPONSE_MODEL
# =============================
#
# Return type (-> Item):
#   - For editor hint + mypy type checking
#   - FastAPI uses it as response_model if not declared
#
# response_model parameter:
#   - Overrides return type
#   - More explicit when input type ≠ output type
#
# Best practice: Use both together
#   - Clear to editor: "returns Item"
#   - Clear to FastAPI: "response matches Item"
# • Combined: clear code + type-safe + auto docs
