"""FastAPI Field - Add validation and metadata to Pydantic model fields"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


# ============================================================================
# 1. WHAT IS Field()?
# ============================================================================
# Field = validation + metadata for model fields
# Use to add validation rules, description, and constraints
# Written inside Pydantic model (not in function like Query/Body)


# ============================================================================
# 2. BASIC EXAMPLE
# ============================================================================


class Item(BaseModel):
    name: str  # required, no validation

    description: Optional[str] = Field(
        default=None,
        title="Item Description",
        max_length=300,  # max 300 characters
    )

    price: float = Field(
        gt=0,  # must be greater than 0
        description="Price must be > 0",
    )

    tax: Optional[float] = None  # optional, no validation


# Valid request example:
# {"name": "Laptop", "description": "Gaming laptop", "price": 999.99}
# FastAPI auto validates

# Invalid request:
# {"name": "Laptop", "price": -10}
# → Error: "price must be greater than zero"


# ============================================================================
# 3. COMMON VALIDATION TYPES
# ============================================================================


class Product(BaseModel):
    # String length validation
    name: str = Field(min_length=3, max_length=50)

    # Number comparison
    price: float = Field(gt=0, lt=1000)  # 0 < price < 1000
    stock: int = Field(ge=0)  # stock >= 0

    # Description for Swagger docs
    category: str = Field(description="Product category")

    # Example value shown in docs
    sku: str = Field(example="SKU-001")

    # Optional with default value
    tags: list[str] = Field(default_factory=list)


# ============================================================================
# 4. Field vs Query/Path
# ============================================================================
# Query/Path/Body = function parameters
# Field = model attributes
#
# @app.get("/items")
# def get_items(q: str = Query(max_length=50)):  ← Query in function
#     pass
#
# class Item(BaseModel):
#     name: str = Field(max_length=50)           ← Field in model
#
# Same syntax, different location


# ============================================================================
# 5. COMPLEX EXAMPLE
# ============================================================================


class User(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=20,
        pattern="^[a-zA-Z0-9_]+$",  # only letters, numbers, underscore
        title="Username",
    )

    email: str = Field(description="Valid email address")

    age: int = Field(ge=18, le=120, title="Age")

    bio: Optional[str] = Field(
        default=None, max_length=500, description="User bio (max 500 characters)"
    )


# ============================================================================
# 6. VALIDATION RULES REFERENCE
# ============================================================================
# gt = greater than
# ge = greater than or equal
# lt = less than
# le = less than or equal
# min_length = minimum string length
# max_length = maximum string length
# pattern = regex pattern
# title = field title
# description = field description
# example = example value
# default_factory = factory to create default value


# ============================================================================
# 7. REAL-WORLD EXAMPLE WITH ENDPOINT
# ============================================================================


class Article(BaseModel):
    title: str = Field(min_length=5, max_length=200, description="Article title")

    content: str = Field(min_length=10, max_length=10000, description="Article content")

    views: int = Field(default=0, ge=0, description="View count")

    rating: float = Field(default=0.0, ge=0, le=5, description="Rating from 0-5")


@app.post("/articles/")
def create_article(article: Article):
    # FastAPI auto validates all fields
    # If validation fails → return error 422 with details
    return {
        "title": article.title,
        "length": len(article.content),
        "rating": article.rating,
    }


# Invalid request:
# {"title": "Bad", "content": "short", "views": -5}
# → Returns multiple validation errors


# ============================================================================
# 8. WHY USE Field()?
# ============================================================================
# Without Field():
#   price: float  → only type check
#   price: float = 0  → type check + default value
#
# With Field():
#   price: float = Field(gt=0)  → type + range + docs
#
# Benefits:
# ✓ Clear code intention
# ✓ More detailed error messages
# ✓ Auto docs (Swagger)
# ✓ Validate input before code runs
# ✓ Type safe
