"""Tests for WebSocket manager."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.websocket_manager import ConnectionManager


@pytest.fixture
def manager():
    """Create a fresh ConnectionManager instance for testing."""
    return ConnectionManager()


# Connection Tests
@pytest.mark.asyncio
async def test_connect_user(manager):
    """Test adding a user connection."""
    mock_ws = AsyncMock()
    user_id = 1

    manager.connect(user_id, mock_ws)

    assert user_id in manager.connections
    assert mock_ws in manager.connections[user_id]
    assert user_id in manager.subscriptions


@pytest.mark.asyncio
async def test_disconnect_user(manager):
    """Test removing a user connection."""
    mock_ws = AsyncMock()
    user_id = 1

    manager.connect(user_id, mock_ws)
    manager.disconnect(user_id, mock_ws)

    # User should no longer be in connections
    assert user_id not in manager.connections


@pytest.mark.asyncio
async def test_multiple_connections_same_user(manager):
    """Test multiple WebSocket connections from same user."""
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    user_id = 1

    manager.connect(user_id, mock_ws1)
    manager.connect(user_id, mock_ws2)

    assert len(manager.connections[user_id]) == 2
    assert mock_ws1 in manager.connections[user_id]
    assert mock_ws2 in manager.connections[user_id]


# Subscription Tests
@pytest.mark.asyncio
async def test_subscribe_to_task(manager):
    """Test subscribing to a task."""
    mock_ws = AsyncMock()
    user_id = 1
    task_id = 100

    # Must connect first
    manager.connect(user_id, mock_ws)
    await manager.subscribe(user_id, mock_ws, task_id)

    assert task_id in manager.subscriptions[user_id][mock_ws]


@pytest.mark.asyncio
async def test_unsubscribe_from_task(manager):
    """Test unsubscribing from a task."""
    mock_ws = AsyncMock()
    user_id = 1
    task_id = 100

    manager.connect(user_id, mock_ws)
    await manager.subscribe(user_id, mock_ws, task_id)
    await manager.unsubscribe(user_id, mock_ws, task_id)

    assert task_id not in manager.subscriptions[user_id][mock_ws]


@pytest.mark.asyncio
async def test_multiple_subscriptions_same_user(manager):
    """Test user subscribed to multiple tasks."""
    mock_ws = AsyncMock()
    user_id = 1
    task_id1 = 100
    task_id2 = 200

    manager.connect(user_id, mock_ws)
    await manager.subscribe(user_id, mock_ws, task_id1)
    await manager.subscribe(user_id, mock_ws, task_id2)

    assert task_id1 in manager.subscriptions[user_id][mock_ws]
    assert task_id2 in manager.subscriptions[user_id][mock_ws]


@pytest.mark.asyncio
async def test_multiple_users_same_task(manager):
    """Test multiple users subscribed to same task."""
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    user_id1 = 1
    user_id2 = 2
    task_id = 100

    manager.connect(user_id1, mock_ws1)
    manager.connect(user_id2, mock_ws2)
    await manager.subscribe(user_id1, mock_ws1, task_id)
    await manager.subscribe(user_id2, mock_ws2, task_id)

    assert task_id in manager.subscriptions[user_id1][mock_ws1]
    assert task_id in manager.subscriptions[user_id2][mock_ws2]


# Broadcast Tests
@pytest.mark.asyncio
async def test_broadcast_to_single_subscriber(manager):
    """Test broadcasting message to single subscriber."""
    mock_ws = AsyncMock()
    user_id = 1
    task_id = 100
    message = {"event": "task_updated", "status": "done"}

    manager.connect(user_id, mock_ws)
    await manager.subscribe(user_id, mock_ws, task_id)
    await manager.broadcast_to_subscribers(task_id, message)

    mock_ws.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_broadcast_to_multiple_subscribers(manager):
    """Test broadcasting message to multiple subscribers."""
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    user_id1 = 1
    user_id2 = 2
    task_id = 100
    message = {"event": "task_updated", "status": "in_progress"}

    manager.connect(user_id1, mock_ws1)
    manager.connect(user_id2, mock_ws2)
    await manager.subscribe(user_id1, mock_ws1, task_id)
    await manager.subscribe(user_id2, mock_ws2, task_id)
    await manager.broadcast_to_subscribers(task_id, message)

    mock_ws1.send_json.assert_called_once_with(message)
    mock_ws2.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_broadcast_to_nonexistent_task(manager):
    """Test broadcasting to task with no subscribers (should not error)."""
    message = {"event": "task_updated", "status": "done"}

    # Should not raise an error
    await manager.broadcast_to_subscribers(9999, message)


@pytest.mark.asyncio
async def test_broadcast_skips_unrelated_subscribers(manager):
    """Test broadcast only sends to relevant task subscribers."""
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    user_id1 = 1
    user_id2 = 2
    task_id1 = 100
    task_id2 = 200
    message = {"event": "task_updated", "status": "done"}

    manager.connect(user_id1, mock_ws1)
    manager.connect(user_id2, mock_ws2)
    await manager.subscribe(user_id1, mock_ws1, task_id1)
    await manager.subscribe(user_id2, mock_ws2, task_id2)

    # Broadcast to task_id1
    await manager.broadcast_to_subscribers(task_id1, message)

    # Only user1's ws should receive
    mock_ws1.send_json.assert_called_once_with(message)
    mock_ws2.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_broadcast_with_send_exception(manager):
    """Test broadcast continues even if one send fails."""
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()

    # First one raises, second one succeeds
    mock_ws1.send_json.side_effect = Exception("Send failed")
    mock_ws2.send_json.side_effect = None

    user_id1 = 1
    user_id2 = 2
    task_id = 100
    message = {"event": "task_updated"}

    manager.connect(user_id1, mock_ws1)
    manager.connect(user_id2, mock_ws2)
    await manager.subscribe(user_id1, mock_ws1, task_id)
    await manager.subscribe(user_id2, mock_ws2, task_id)

    # Should not raise, but should continue to next subscriber
    await manager.broadcast_to_subscribers(task_id, message)

    # Second subscriber should still be called
    mock_ws2.send_json.assert_called_once_with(message)


# Complex Scenarios
@pytest.mark.asyncio
async def test_broadcast_with_complex_message(manager):
    """Test broadcasting complex message structure."""
    mock_ws = AsyncMock()
    user_id = 1
    task_id = 100
    message = {
        "event": "task_updated",
        "task": {
            "id": 100,
            "title": "Test task",
            "status": "in_progress",
            "tags": ["urgent", "backend"],
        },
        "metadata": {"updated_by": user_id, "timestamp": "2024-01-01"},
    }

    manager.connect(user_id, mock_ws)
    await manager.subscribe(user_id, mock_ws, task_id)
    await manager.broadcast_to_subscribers(task_id, message)

    mock_ws.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_subscribe_then_resubscribe_same_task(manager):
    """Test subscribing to same task twice (idempotent)."""
    mock_ws = AsyncMock()
    user_id = 1
    task_id = 100

    manager.connect(user_id, mock_ws)
    await manager.subscribe(user_id, mock_ws, task_id)
    await manager.subscribe(user_id, mock_ws, task_id)

    # Should still only have one subscription
    assert task_id in manager.subscriptions[user_id][mock_ws]
    assert len(manager.subscriptions[user_id][mock_ws]) == 1


@pytest.mark.asyncio
async def test_connection_and_subscription_lifecycle(manager):
    """Test full lifecycle: connect → subscribe → broadcast → unsubscribe → disconnect."""
    mock_ws = AsyncMock()
    user_id = 1
    task_id = 100
    message = {"event": "task_updated", "status": "done"}

    # Connect
    manager.connect(user_id, mock_ws)
    assert user_id in manager.connections

    # Subscribe
    await manager.subscribe(user_id, mock_ws, task_id)
    assert task_id in manager.subscriptions[user_id][mock_ws]

    # Broadcast
    await manager.broadcast_to_subscribers(task_id, message)
    mock_ws.send_json.assert_called_once()

    # Unsubscribe
    await manager.unsubscribe(user_id, mock_ws, task_id)
    assert task_id not in manager.subscriptions[user_id][mock_ws]

    # Disconnect
    manager.disconnect(user_id, mock_ws)
    assert user_id not in manager.connections
