# Handle Errors - Return clear errors to client
#
# Why needed:
# Client sends wrong data → backend must report clearly
# Cannot stay silent!
#
# Who is "Client"?
# - Frontend (browser)
# - Mobile app
# - Another backend
# - IoT device
# All need clear errors


from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()


# BASIC EXAMPLE: 404 Not Found
# =============================

fake_items = {"foo": "Foo Item", "bar": "Bar Item"}


@app.get("/items/{item_id}")
async def get_item(item_id: str):
    if item_id not in fake_items:
        # Raise error instead of return
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": fake_items[item_id]}


# Test:
# GET /items/foo → {"item": "Foo Item"} (200)
# GET /items/xyz → {"detail": "Item not found"} (404)


# WHY RAISE instead of RETURN?
# ============================
# raise = stop execution immediately
# return = continue execution
#
# Raise is better because:
# 1. Stops further processing
# 2. No nested if-else hell
# 3. FastAPI handles response automatically


# COMMON ERROR SCENARIOS
# ======================


class Item(BaseModel):
    name: str
    price: float


@app.get("/items-int/{item_id}")
async def get_item_by_id(item_id: int):
    if item_id < 1:
        raise HTTPException(status_code=400, detail="ID must be positive")
    if item_id > 1000:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, "name": "Some item"}


@app.post("/items/")
async def create_item(item: Item):
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    return {"created": item}


# ERROR DETAIL CAN BE DICT (not just string)
# ===========================================


@app.post("/users/")
async def create_user(email: str, username: str):
    if "@" not in email:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid email format",
                "field": "email",
                "received": email,
            },
        )
    return {"email": email, "username": username}


# Response:
# {
#     "detail": {
#         "error": "Invalid email format",
#         "field": "email",
#         "received": "invalid"
#     }
# }
# (FastAPI auto-converts to JSON)


# AUTHENTICATION ERROR (401)
# ==========================


@app.get("/secret/")
async def get_secret(token: str | None = None):
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token != "secret123":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Secret data"}


# CUSTOM EXCEPTION + HANDLER
# ==========================
# Use when you have app-specific errors


class ItemOutOfStock(Exception):
    def __init__(self, item_id: int, available: int):
        self.item_id = item_id
        self.available = available


@app.exception_handler(ItemOutOfStock)
async def item_out_of_stock_handler(request: Request, exc: ItemOutOfStock):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Out of stock",
            "item_id": exc.item_id,
            "available": exc.available,
        },
    )


@app.post("/buy/{item_id}")
async def buy_item(item_id: int, quantity: int):
    available = 5  # Simulated
    if quantity > available:
        raise ItemOutOfStock(item_id, available)
    return {"success": True}


# OVERRIDE FASTAPI'S DEFAULT ERROR HANDLER
# ==========================================
# FastAPI validates input and returns:
# {
#     "detail": [
#         {
#             "loc": ["path", "item_id"],
#             "msg": "value is not a valid integer"
#         }
#     ]
# }
#
# You can override to return custom format


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Return plain text instead of JSON
    errors = []
    for error in exc.errors():
        field = error["loc"][-1]  # Get field name
        msg = error["msg"]
        errors.append(f"Field '{field}': {msg}")

    return PlainTextResponse(content="\n".join(errors), status_code=400)


# Instead of JSON, returns:
# Field 'item_id': value is not a valid integer
# Field 'name': field required


# RE-RAISE WITH CUSTOM HANDLER
# =============================
# Sometimes you want to:
# 1. Log the error
# 2. Modify it slightly
# 3. Let default handler process it

http_exception_handler = None  # Will be set below


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Do custom logging
    print(f"ERROR {exc.status_code}: {exc.detail}")

    # Call default handler
    from fastapi.exception_handlers import http_exception_handler as default_handler

    return await default_handler(request, exc)


# IMPORTANT: Body access in error handler
# ========================================
# You can get request body to log what went wrong


@app.exception_handler(RequestValidationError)
async def validation_with_body_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation failed",
            "errors": exc.errors(),
            "received_data": body.decode() if body else None,
        },
    )


# SUMMARY
# =======
# 1. Use raise HTTPException, not return
# 2. Pick correct status code (400, 401, 403, 404, 500...)
# 3. detail can be string or dict
# 4. Custom exceptions for app-specific logic
# 5. @app.exception_handler() to override behavior
# 6. Don't expose internal error details in production!
