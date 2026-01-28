"""FastAPI Nested Models - Model inside model, list, dict"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Set

app = FastAPI()


# ============================================================================
# 1. LIST OF STRINGS
# ============================================================================


class Tag(BaseModel):
    # tags: list[str] = array of strings
    tags: list[str]  # ["red", "green", "blue"]


@app.post("/tags/")
def add_tags(tag: Tag):
    # FastAPI knows: tags is an array, each element is string
    # If you write tags: list (without [str])
    # FastAPI doesn't know what's inside, docs will be ugly
    return {"tags": tag.tags}


# ============================================================================
# 2. COMMON TYPES
# ============================================================================
# str          → text ("hello")
# int          → integer (42)
# float        → decimal (3.14)
# bool         → true/false
# list[str]    → array of text (["a", "b"])
# list[int]    → array of numbers ([1, 2, 3])
# set[str]     → array no duplicates ({"a", "b"})
# dict[str, int] → key-value ({"name": 1})


# ============================================================================
# 3. SET - ARRAY WITHOUT DUPLICATES
# ============================================================================


class Tags(BaseModel):
    # set[str] = array that doesn't allow duplicate values
    # ["a", "a", "c"] automatically becomes {"a", "c"}
    tags: set[str]


@app.post("/tags_unique/")
def add_unique_tags(data: Tags):
    # If client sends: ["apple", "apple", "banana"]
    # In code: data.tags = {"apple", "banana"}
    return {"unique_tags": list(data.tags)}


# ============================================================================
# 4. NESTED MODEL (Model inside model)
# ============================================================================


# Child model first
class Image(BaseModel):
    url: str
    width: int
    height: int


# Parent model
class Product(BaseModel):
    name: str
    price: float
    image: Image  # embed Image here


@app.post("/products/")
def create_product(product: Product):
    # JSON sent:
    # {
    #   "name": "Laptop",
    #   "price": 999.99,
    #   "image": {
    #     "url": "https://example.com/laptop.jpg",
    #     "width": 800,
    #     "height": 600
    #   }
    # }

    # In code:
    # product.name = "Laptop"
    # product.image.url = "https://..."
    # product.image.width = 800
    return {"name": product.name, "image_url": product.image.url}


# ============================================================================
# 5. OPTIONAL NESTED MODEL
# ============================================================================


class ProductOptional(BaseModel):
    name: str
    price: float
    image: Image | None = None  # can have image or not


@app.post("/products_optional/")
def create_product_optional(product: ProductOptional):
    # Client can send without image
    if product.image:
        return {"name": product.name, "has_image": True}
    return {"name": product.name, "has_image": False}


# ============================================================================
# 6. LIST OF NESTED MODEL
# ============================================================================


class Item(BaseModel):
    name: str
    price: float


class Order(BaseModel):
    order_id: str
    items: List[Item]  # array containing Item objects


@app.post("/orders/")
def create_order(order: Order):
    # JSON:
    # {
    #   "order_id": "ORD-001",
    #   "items": [
    #     {"name": "Laptop", "price": 999.99},
    #     {"name": "Mouse", "price": 29.99}
    #   ]
    # }

    total = sum(item.price for item in order.items)
    return {"order": order.order_id, "count": len(order.items), "total": total}


# ============================================================================
# 7. MULTI-LEVEL NESTED (Model nested multiple levels)
# ============================================================================


class Address(BaseModel):
    street: str
    city: str
    country: str


class Customer(BaseModel):
    name: str
    email: str
    address: Address  # nested level 1


class Invoice(BaseModel):
    invoice_id: str
    customer: Customer  # nested level 2
    items: List[Item]  # list nested level 1


@app.post("/invoices/")
def create_invoice(invoice: Invoice):
    # Access from deep:
    # invoice.customer.address.city
    return {
        "invoice": invoice.invoice_id,
        "customer_city": invoice.customer.address.city,
        "total_items": len(invoice.items),
    }


# ============================================================================
# 8. BODY IS LIST DIRECTLY
# ============================================================================


@app.post("/images/")
def upload_images(images: List[Image]):
    # Request body is array directly:
    # [
    #   {"url": "...", "width": 800, "height": 600},
    #   {"url": "...", "width": 400, "height": 300}
    # ]

    return {
        "count": len(images),
        "total_pixels": sum(img.width * img.height for img in images),
    }


# ============================================================================
# 9. DICT - ARBITRARY KEY-VALUE
# ============================================================================


class WeightConfig(BaseModel):
    # dict[str, float] = {key: value}
    # JSON: {"item1": 0.5, "item2": 1.2}
    weights: Dict[str, float]


@app.post("/weights/")
def set_weights(config: WeightConfig):
    # Access: config.weights["item1"] = 0.5
    return {"weights": config.weights}


# ============================================================================
# 10. TIP: DICT AS BODY
# ============================================================================


@app.post("/metadata/")
def set_metadata(metadata: Dict[str, str]):
    # Request body is dict directly:
    # {"key1": "value1", "key2": "value2"}
    return {"received": metadata}


# ============================================================================
# MEMORY RULES
# ============================================================================
# 1. Child model first, parent model after
# 2. list[Model] = array containing that model
# 3. Model | None = optional model
# 4. dict[str, float] = key is string, value is float
# 5. set[str] = array no duplicates, strings only
# 6. Can nest infinitely deep
# 7. FastAPI auto validates entire nested structure
