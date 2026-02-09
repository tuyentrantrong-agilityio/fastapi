"""
FastAPI Async Examples - Short & Concise
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

from fastapi import FastAPI, BackgroundTasks

app = FastAPI()
executor = ThreadPoolExecutor()


# 1. BASIC ASYNC ENDPOINT
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Async endpoint - returns immediately without blocking"""
    await asyncio.sleep(1)  # Simulate I/O operation
    return {"user_id": user_id, "name": "John"}


# 2. SYNC vs ASYNC
@app.get("/sync")
def sync_endpoint():
    """Sync endpoint - blocks thread"""
    time.sleep(2)  # Blocks the thread
    return {"message": "Done (blocking)"}


@app.get("/async")
async def async_endpoint():
    """Async endpoint - doesn't block"""
    await asyncio.sleep(2)  # Doesn't block other requests
    return {"message": "Done (non-blocking)"}


# 3. MULTIPLE CONCURRENT OPERATIONS
@app.get("/concurrent")
async def concurrent_operations():
    """Run multiple async operations concurrently"""

    async def fetch_user():
        await asyncio.sleep(1)
        return {"user": "Alice"}

    async def fetch_posts():
        await asyncio.sleep(1)
        return {"posts": [1, 2, 3]}

    # Run both concurrently (1 second total, not 2)
    user, posts = await asyncio.gather(fetch_user(), fetch_posts())

    return {"user": user, "posts": posts}


# 4. BACKGROUND TASKS
@app.post("/send-email")
async def send_email(email: str, background_tasks: BackgroundTasks):
    """Add task to run in background"""

    async def send_email_async(email_addr: str):
        await asyncio.sleep(2)
        print(f"Email sent to {email_addr}")

    background_tasks.add_task(send_email_async, email)
    return {"message": "Email will be sent in background"}


# 5. ASYNC GENERATOR
@app.get("/stream")
async def stream_data():
    """Stream data asynchronously"""

    async def data_generator():
        for i in range(5):
            await asyncio.sleep(0.5)
            yield f"data {i}"

    data = []
    async for item in data_generator():
        data.append(item)

    return {"stream": data}


# 6. TIMEOUT HANDLING
@app.get("/with-timeout")
async def with_timeout():
    """Handle timeout with asyncio.wait_for"""

    async def slow_operation():
        await asyncio.sleep(5)
        return "completed"

    try:
        result = await asyncio.wait_for(slow_operation(), timeout=2)
    except asyncio.TimeoutError:
        return {"error": "Operation timeout"}

    return {"result": result}


# 7. MIXED SYNC & ASYNC (CPU-bound work)
@app.get("/cpu-work/{n}")
async def cpu_intensive_work(n: int):
    """Offload CPU-bound work to thread pool"""

    def heavy_computation(num):
        time.sleep(2)  # CPU-bound work
        return num**2

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, heavy_computation, n)

    return {"result": result}


# 8. ERROR HANDLING IN ASYNC
@app.get("/async-error")
async def handle_async_error():
    """Handle errors in async operations"""

    async def fetch_data():
        await asyncio.sleep(1)
        raise ValueError("Data fetch failed")

    try:
        result = await fetch_data()
    except ValueError as e:
        return {"error": str(e)}

    return {"result": result}


# 9. ASYNC WITH MULTIPLE REQUESTS
@app.get("/batch-fetch")
async def batch_fetch(ids: List[int]):
    """Fetch multiple items concurrently"""

    async def fetch_item(item_id: int):
        await asyncio.sleep(0.5)
        return {"id": item_id, "data": f"Item {item_id}"}

    # Fetch all items concurrently
    results = await asyncio.gather(*[fetch_item(id) for id in ids])

    return {"items": results}


# 10. SEMAPHORE - LIMIT CONCURRENT OPERATIONS
@app.get("/limited-concurrent")
async def limited_concurrent():
    """Limit number of concurrent operations"""

    semaphore = asyncio.Semaphore(2)  # Max 2 concurrent

    async def limited_task(task_id: int):
        async with semaphore:
            await asyncio.sleep(1)
            return f"Task {task_id} done"

    results = await asyncio.gather(*[limited_task(i) for i in range(5)])

    return {"results": results}
