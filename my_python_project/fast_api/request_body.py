"""FastAPI Request Body - Receive JSON data from clients"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()


# ============================================================================
# BASICS: What's a request body?
# ============================================================================
# Request body = JSON data client sends in POST/PUT requests
# Path: /items/{id} - WHICH item?
# Query: ?skip=0&limit=10 - HOW MANY items?
# Body: POST {data} - CREATE what?


# ============================================================================
# 1. SIMPLE MODEL
# ============================================================================


class Item(BaseModel):
    # Pydantic model = blueprint for JSON data
    name: str
    price: float
    description: Optional[str] = None  # optional = can be null or missing
    tax: Optional[float] = None


@app.post("/items/")
def create_item(item: Item):
    # FastAPI sees Pydantic model → automatically treats as request body
    # Validates JSON against model, converts to Python object
    return item


# ============================================================================
# 2. ACCESSING FIELDS
# ============================================================================


@app.post("/items/buy/")
def buy_item(item: Item):
    # Access fields like normal attributes
    total = item.price + (item.tax or 0)
    return {"item": item.name, "total": total}


# ============================================================================
# 3. PATH + BODY
# ============================================================================


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    # FastAPI knows: {item_id} in URL = path param
    # item = Pydantic model = body
    return {"id": item_id, "name": item.name}


# ============================================================================
# 4. BODY + QUERY
# ============================================================================


@app.post("/items_search/")
def search_items(item: Item, q: Optional[str] = None, skip: int = 0):
    # item = body (Pydantic model)
    # q, skip = query params (primitives with defaults)
    return {"item": item.name, "search": q, "skip": skip}


# ============================================================================
# 5. NESTED MODELS
# ============================================================================


class Address(BaseModel):
    street: str
    city: str


class User(BaseModel):
    name: str
    address: Address  # nested model


@app.post("/users/")
def create_user(user: User):
    # Access nested: user.address.city
    return {"name": user.name, "city": user.address.city}


# ============================================================================
# 6. LISTS
# ============================================================================


class Order(BaseModel):
    order_id: str
    items: List[Item]  # list of Item objects


@app.post("/orders/")
def create_order(order: Order):
    # Validate: each item in list must match Item model
    total = sum(item.price for item in order.items)
    return {"order": order.order_id, "total": total, "count": len(order.items)}


# ============================================================================
# 7. OPTIONAL FIELDS & DEFAULTS
# ============================================================================


class Product(BaseModel):
    name: str  # required
    price: float  # required
    stock: int = 10  # optional, default 10
    desc: Optional[str] = None  # optional, default None


@app.post("/products/")
def add_product(p: Product):
    # Only need name + price in JSON, rest uses defaults
    return p


# ============================================================================
# 8. VALIDATION - AUTOMATIC
# ============================================================================
# Pydantic auto-validates:
# - Field types (price: float expects float/int, not string)
# - Required fields (missing = error 422)
# - Optional fields (can be null or missing)
#
# Bad JSON example:
# {"name": "Item", "price": "abc"} → ERROR (price should be float)
# {"name": "Item"} → ERROR (price required)
# {"name": "Item", "price": 99.9} → OK


# ============================================================================
# 9. COMPLEX EXAMPLE
# ============================================================================


class Contact(BaseModel):
    email: str
    phone: Optional[str] = None


class Checkout(BaseModel):
    customer: str
    contact: Contact  # nested
    items: List[Item]  # list
    notes: Optional[str] = None  # optional
    rush: bool = False  # optional, default False


@app.post("/checkout/")
def process_checkout(order: Checkout):
    # Everything auto-validated by Pydantic
    total = sum(item.price for item in order.items)
    return {
        "customer": order.customer,
        "email": order.contact.email,
        "total": total,
        "rush": order.rush,
    }


# ============================================================================
# QUICK RULES
# ============================================================================
# 1. Pydantic model → request body
# 2. Primitive + default value → query param
# 3. {variable} in path → path param
# 4. Primitive without default → query param (or error if can't determine)
# 5. Optional[type] = None → can be null or missing
# 6. type = value → optional with default
# 7. type (no default) → required
#
# Example:
# @app.post("/path/{id}")
# def func(id: int, item: Item, q: str = None):
#     id → path param (from {id})
#     item → body (Pydantic model)
#     q → query param (primitive + default)
