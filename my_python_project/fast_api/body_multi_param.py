"""FastAPI - Multiple request bodies and complex parameters"""

from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()


# ============================================================================
# PROBLEM: Need to send multiple JSON objects in one request?
# ============================================================================
# By default, FastAPI expects one Pydantic model = one body
# What if you need 2+ bodies?
# Solution: Use Body() to mark multiple models as body parameters


# ============================================================================
# 1. MULTIPLE BODIES WITH Body()
# ============================================================================


class Item(BaseModel):
    name: str
    price: float


class User(BaseModel):
    username: str
    email: str


@app.post("/buy/")
def create_purchase(user: User, item: Item):
    # Two Pydantic models → FastAPI confused, which one is body?
    # This won't work as expected!
    return {"buyer": user.username, "product": item.name}


@app.post("/buy_fixed/")
def create_purchase_fixed(user: User = Body(...), item: Item = Body(...)):
    # Body(...) = explicitly mark as body parameters
    # Now FastAPI expects JSON like:
    # {
    #   "user": {"username": "...", "email": "..."},
    #   "item": {"name": "...", "price": ...}
    # }
    return {"buyer": user.username, "product": item.name}


# ============================================================================
# 2. MULTIPLE BODIES - ACTUAL EXAMPLE
# ============================================================================


class Credentials(BaseModel):
    username: str
    password: str


class Profile(BaseModel):
    full_name: str
    age: int
    bio: Optional[str] = None


@app.post("/register/")
def register(credentials: Credentials = Body(...), profile: Profile = Body(...)):
    # Client sends:
    # {
    #   "credentials": {"username": "john", "password": "secret"},
    #   "profile": {"full_name": "John Doe", "age": 30, "bio": "..."}
    # }
    return {"user": credentials.username, "name": profile.full_name}


# ============================================================================
# 3. BODY + PATH + QUERY
# ============================================================================


@app.put("/users/{user_id}")
def update_user(
    user_id: int,  # path
    profile: Profile = Body(...),  # body
    notify: bool = False,  # query
):
    # URL: PUT /users/42?notify=true
    # Body: {"full_name": "...", "age": ...}
    return {"user_id": user_id, "updated": profile.full_name, "notified": notify}


# ============================================================================
# 4. MULTIPLE BODIES + SINGLE PRIMITIVE
# ============================================================================


class Order(BaseModel):
    order_id: str
    total: float


class Shipping(BaseModel):
    address: str
    phone: str


@app.post("/ship/")
def ship_order(
    order: Order = Body(...),
    shipping: Shipping = Body(...),
    expedited: bool = False,  # NOT a body, just a query param
):
    # JSON:
    # {
    #   "order": {...},
    #   "shipping": {...}
    # }
    # Query: ?expedited=true
    return {"order": order.order_id, "shipping": shipping.address, "fast": expedited}


# ============================================================================
# 5. EMBED SINGLE BODY (Less common but useful)
# ============================================================================


class Payment(BaseModel):
    amount: float
    method: str


@app.post("/pay/")
def make_payment(payment: Payment):
    # By default, expects: {"amount": 100, "method": "card"}
    # Client can pass directly without wrapper
    return payment


@app.post("/pay_embedded/")
def make_payment_embedded(payment: Payment = Body(..., embed=True)):
    # With embed=True, expects: {"payment": {"amount": 100, "method": "card"}}
    # Forces the model to be nested under its own name
    # Useful when you want consistent nested structure
    return payment


# ============================================================================
# 6. REAL EXAMPLE: CHECKOUT WITH MULTIPLE DATA
# ============================================================================


class CartItem(BaseModel):
    id: int
    qty: int
    price: float


class Cart(BaseModel):
    items: List[CartItem]
    total: float


class ShipTo(BaseModel):
    name: str
    address: str
    zip: str


class PaymentInfo(BaseModel):
    card_number: str
    cvv: str
    exp: str


@app.post("/checkout/")
def checkout(
    cart: Cart = Body(...),
    shipping: ShipTo = Body(...),
    payment: PaymentInfo = Body(...),
    save_address: bool = False,
):
    # Request JSON:
    # {
    #   "cart": {
    #     "items": [{"id": 1, "qty": 2, "price": 50}],
    #     "total": 100
    #   },
    #   "shipping": {"name": "John", "address": "123 St", "zip": "12345"},
    #   "payment": {"card_number": "...", "cvv": "...", "exp": "..."}
    # }
    # ?save_address=true

    return {
        "order_total": cart.total,
        "ship_to": shipping.address,
        "saved": save_address,
    }


# ============================================================================
# 7. WHY USE Body()?
# ============================================================================
# Without Body():
#   - One Pydantic model = request body
#   - Multiple Pydantic models = confusing, might not work
#
# With Body(...):
#   - Explicitly says "this is a body parameter"
#   - Can have multiple bodies
#   - Each gets its own JSON object wrapper
#
# Body(..., embed=True):
#   - Forces wrapping even for single model
#   - Makes JSON structure consistent
#   - Good for API consistency


# ============================================================================
# QUICK TIPS
# ============================================================================
# - One model, no Body() → {"field": "value"}
# - One model, Body(embed=True) → {"modelname": {"field": "value"}}
# - Multiple models, Body() → {"model1": {...}, "model2": {...}}
# - Path params: always work with Body()
# - Query params: always work with Body()
