"""WebSocket endpoint for real-time task updates with dynamic subscriptions"""

import logging
from fastapi import APIRouter, WebSocket
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.websocket_manager import manager
from ...core.security import decode_token
from ...db.session import AsyncSessionLocal
from ...models.task import Task

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for realtime task updates with dynamic subscriptions

    Usage: ws://localhost:8000/ws?token=<jwt_token>

    Protocol:
    - Client sends: {"action": "subscribe", "task_id": 1}
    - Server responds: {"event": "subscription_confirmed", "task_id": 1}
    - Server push: {"event": "task_updated", "task_id": 1, "status": "completed", ...}
    """

    # STEP 0: Extract token from query params (manual, not Query dependency)
    token = websocket.query_params.get("token")
    if not token:
        logger.warning("WebSocket connection attempted without token")
        await websocket.close(code=1008, reason="Missing token")
        return

    # STEP 1: Authenticate JWT Token
    try:
        payload = decode_token(token)
        email = payload.get("sub")

        if not email:
            logger.warning(f"WebSocket auth failed: no sub in token - {payload}")
            await websocket.close(code=1008, reason="Invalid token")
            return

        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            from ...models.user import User

            result = await session.execute(select(User).where(User.email == email))
            user = result.scalars().first()
            if not user:
                logger.warning(f"WebSocket auth failed: user {email} not found")
                await websocket.close(code=1008, reason="User not found")
                return
            user_id = user.id

    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        await websocket.close(code=1008, reason="Auth failed")
        return

    # STEP 2: Accept connection (only after auth succeeds)
    await websocket.accept()
    await websocket.send_json(
        {
            "event": "connected",
            "user_id": user_id,
            "message": "WebSocket connected successfully",
        }
    )

    # STEP 3: Add to manager
    manager.connect(user_id, websocket)
    logger.info(f"User {user_id} connected to WebSocket")

    try:
        # STEP 4: Listen for messages
        while True:
            msg = await websocket.receive_json()
            action = msg.get("action")
            task_id = msg.get("task_id")

            if action == "subscribe":
                # [OK] STEP 1: Check ownership HERE (in router layer, not in manager)
                try:
                    # Verify task exists + user owns it
                    async with AsyncSessionLocal() as session:
                        result = await session.execute(
                            select(Task).where(Task.id == task_id)
                        )
                        task = result.scalars().first()

                    if not task:
                        await websocket.send_json(
                            {
                                "event": "subscription_error",
                                "task_id": task_id,
                                "error": "Task not found",
                            }
                        )
                        logger.debug(
                            f"User {user_id} tried to subscribe to non-existent task {task_id}"
                        )
                    elif task.user_id != user_id:
                        await websocket.send_json(
                            {
                                "event": "subscription_error",
                                "task_id": task_id,
                                "error": "You don't own this task",
                            }
                        )
                        logger.warning(
                            f"User {user_id} tried to subscribe to task {task_id} owned by user {task.user_id}"
                        )
                    else:
                        # [OK] STEP 2: Ownership verified -> call manager
                        await manager.subscribe(user_id, websocket, task_id)
                        await websocket.send_json(
                            {
                                "event": "subscription_confirmed",
                                "task_id": task_id,
                                "message": f"Subscribed to task {task_id}",
                            }
                        )
                except Exception as e:
                    logger.error(f"Subscribe error for user {user_id}: {e}")
                    await websocket.send_json(
                        {"event": "error", "error": f"Subscription failed: {str(e)}"}
                    )

            elif action == "unsubscribe":
                # Client stops listening
                await manager.unsubscribe(user_id, websocket, task_id)
                await websocket.send_json(
                    {"event": "unsubscription_confirmed", "task_id": task_id}
                )
                logger.debug(f"User {user_id} unsubscribed from task {task_id}")

            else:
                await websocket.send_json(
                    {"event": "error", "error": f"Unknown action: {action}"}
                )

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")

    finally:
        # STEP 5: Cleanup on disconnect
        manager.disconnect(user_id, websocket)
        logger.info(f"User {user_id} disconnected from WebSocket")
