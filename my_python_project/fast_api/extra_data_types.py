"""
FastAPI Extra Data Types

From beginning you use basic types: int, str, float, bool
But reality needs many other types:
- UUID: unique ID that's very long
- datetime: date + time
- date: only date
- time: only time
- timedelta: time duration
- Decimal: money (more precise than float)
- bytes: file/binary data

FastAPI advantages:
✓ Client sends string -> FastAPI auto converts to Python type
✓ Auto validates (checks correct/wrong)
✓ Auto generates docs in /docs
✓ You code normally, no need to parse manually
"""

from datetime import datetime, date, time, timedelta
from typing import Annotated
from uuid import UUID
from decimal import Decimal
from fastapi import FastAPI

app = FastAPI()


# ============================================================
# 1. UUID - VERY LONG ID, ALMOST NEVER DUPLICATES
# ============================================================


@app.get("/items/{item_id}/")
async def read_item(item_id: UUID):
    """
    UUID = very long ID almost never duplicates

    Example: 550e8400-e29b-41d4-a716-446655440000

    FastAPI auto:
    ✓ Check format correct or wrong
    ✓ If wrong -> return error 422
    ✓ If correct -> convert to UUID object

    You code:
    """
    return {
        "item_id": item_id,
        "item_type": type(item_id).__name__,
    }


# ============================================================
# 2. DATETIME - DATE + TIME
# ============================================================


@app.post("/orders/")
async def create_order(
    order_time: datetime,
):
    """
    datetime = date + time (example: 2026-01-28T10:30:00)

    Use when need to know:
    - Moment order placed
    - Moment processing started
    - Timestamp of event

    Client sends:
        POST /orders/
        {"order_time": "2026-01-28T10:30:00"}

    Python receives datetime object -> can do math:
    """
    end_time = order_time + timedelta(hours=1)
    return {
        "order_time": order_time,
        "expected_delivery": end_time,
    }


# ============================================================
# 3. DATE - ONLY DATE (NO TIME)
# ============================================================


@app.post("/birthdays/")
async def register_birthday(
    birth_date: date,
):
    """
    date = only date (example: 2026-01-28)

    Use when:
    - Birth date
    - Expiration date
    - Report date

    No need for hours/minutes/seconds
    """
    today = date.today()
    age = today.year - birth_date.year
    return {
        "birth_date": birth_date,
        "age": age,
    }


# ============================================================
# 4. TIME - ONLY TIME (NO DATE)
# ============================================================


@app.post("/schedule/")
async def set_schedule(
    open_time: time,
    close_time: time,
):
    """
    time = only time (example: 09:30:00)

    Use when:
    - Store opening time
    - Store closing time
    - Recurring time daily (alarm, cron job)

    No need specific date
    """
    return {
        "open_time": open_time,
        "close_time": close_time,
        "message": "Store open 09:30 to 18:00 every day",
    }


# ============================================================
# 5. TIMEDELTA - TIME DURATION
# ============================================================


@app.post("/tasks/")
async def create_task(
    duration: timedelta,
):
    """
    timedelta = time duration (how long, how much delay)

    Use when:
    - Task runs how long
    - Wait how long
    - Delay how long
    - Retry after how long

    Client sends seconds:
        {"duration": 7200}

    FastAPI converts to:
        timedelta(seconds=7200) = 2 hours
    """
    start = datetime.now()
    end = start + duration
    return {
        "start_time": start,
        "duration_seconds": duration.total_seconds(),
        "end_time": end,
    }


# ============================================================
# 6. DECIMAL - MONEY (MORE PRECISE THAN FLOAT)
# ============================================================


@app.post("/prices/")
async def set_price(
    price: Decimal,
):
    """
    Decimal = decimal number precise (use for money)

    Why not use float?
    - float has rounding error (0.1 + 0.2 != 0.3)
    - Decimal 100% accurate

    Always use Decimal for:
    - Money
    - Price
    - Financial calculations
    """
    total = price * 2
    return {
        "unit_price": price,
        "total_for_2_units": total,
        "type": type(price).__name__,
    }


# ============================================================
# 7. BYTES - FILE / BINARY DATA
# ============================================================


@app.post("/upload/")
async def upload_file(
    data: bytes,
):
    """
    bytes = binary data (file, image, video)

    Use when:
    - Upload file
    - Send image
    - Send binary data

    FastAPI auto decodes from base64 string
    """
    return {
        "size_bytes": len(data),
        "first_10_bytes": data[:10],
    }


# ============================================================
# 8. MIX TYPES (Combine multiple types)
# ============================================================


@app.post("/bookings/")
async def create_booking(
    booking_date: date,
    start_time: time,
    duration: timedelta,
    price: Decimal,
):
    """
    Real-world - 1 endpoint uses many different types

    Example restaurant table booking:
    - booking_date: which date (2026-01-28)
    - start_time: which time (19:30:00)
    - duration: stay how long (2 hours)
    - price: how much (99.99)
    """
    booking_datetime = datetime.combine(booking_date, start_time)
    end_datetime = booking_datetime + duration

    return {
        "booking_date": booking_date,
        "start_time": start_time,
        "duration_minutes": int(duration.total_seconds() / 60),
        "end_time": end_datetime.time(),
        "total_price": price,
    }


# ============================================================
# 9. OPTIONAL - CAN BE PRESENT OR NOT
# ============================================================


@app.post("/events/")
async def create_event(
    name: str,
    start_date: date,
    end_date: date | None = None,
    reminder_time: time | None = None,
):
    """
    Use | None when field is optional

    Example:
    - end_date: does event have deadline or forever?
    - reminder_time: do you need reminder or not?

    Client can send or not send
    """
    result = {
        "name": name,
        "start_date": start_date,
    }

    if end_date:
        duration = (end_date - start_date).days
        result["end_date"] = end_date
        result["duration_days"] = duration

    if reminder_time:
        result["reminder_time"] = reminder_time

    return result


# ============================================================
# SUMMARY
# ============================================================
"""
📌 UUID
   - Very long ID almost no duplicates
   - Format: 550e8400-e29b-41d4-a716-446655440000

📌 datetime
   - Date + time + minutes + seconds
   - Format: 2026-01-28T10:30:00
   - Use for: timestamp, event

📌 date
   - Only date (no time)
   - Format: 2026-01-28
   - Use for: birth date, expiration

📌 time
   - Only time (no date)
   - Format: 10:30:00
   - Use for: opening hours, alarm

📌 timedelta
   - Time duration
   - Format: seconds
   - Use for: duration, timeout

📌 Decimal
   - Precise decimal number
   - Always use for money, not float

📌 bytes
   - Binary data
   - Use for: file, image

💡 FastAPI auto converts from string -> Python type
💡 You receive real object, can do math
💡 Auto validates format, wrong -> 422
"""
