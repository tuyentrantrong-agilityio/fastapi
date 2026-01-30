# JSON Compatible Encoder - Convert Python data → JSON
#
# Problem: JSON doesn't understand datetime, UUID, Decimal, set, Pydantic model...
# Solution: Use jsonable_encoder() to convert to dict

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import json

app = FastAPI()


# EXAMPLE 1: Datetime
# ==================


class Event(BaseModel):
    title: str
    created_at: datetime


@app.post("/events/")
async def create_event(event: Event):
    # Wrong: return event (datetime not serializable)
    # Correct:
    event_data = jsonable_encoder(event)
    return event_data
    # Response: {"title": "...", "created_at": "2026-01-30T10:30:00"}


# EXAMPLE 2: Decimal, UUID, Set
# ============================


class Product(BaseModel):
    id: UUID
    name: str
    price: Decimal
    tags: set[str]


product = Product(
    id=uuid4(), name="Apple", price=Decimal("9.99"), tags={"fruit", "organic"}
)
data = jsonable_encoder(product)
# UUID→string, Decimal→number, set→list


# EXAMPLE 3: Nested models
# ========================


class Address(BaseModel):
    city: str
    zipcode: str


class User(BaseModel):
    name: str
    created_at: datetime
    address: Address


user = User(
    name="Tuyen",
    created_at=datetime.now(),
    address=Address(city="Hanoi", zipcode="100000"),
)
data = jsonable_encoder(user)
# Auto handle nested + datetime


# EXAMPLE 4: List models
# ======================

items = [
    Product(id=uuid4(), name="Apple", price=Decimal("1.5"), tags={"fruit"}),
    Product(id=uuid4(), name="Orange", price=Decimal("2.0"), tags={"fruit"}),
]
items_data = jsonable_encoder(items)
# All converted


# IMPORTANT
# =========
# 1. jsonable_encoder() → dict (not JSON string)
# 2. FastAPI calls it automatically when returning from endpoint
# 3. Use manually when need to save to database before response
# 4. Supports: datetime→string, UUID→string, Decimal→float, set→list...
