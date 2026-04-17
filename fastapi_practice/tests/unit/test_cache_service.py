"""
Unit tests for cache service.

Tests cover:
- Cache GET (miss and hit scenarios)
- Cache SET with TTL
- Cache invalidation on update
- Cache key generation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_get_miss():
    """Test cache GET when key doesn't exist (cache miss).

    Scenario:
    - Redis returns None (key not found)
    - Expected: Cache miss returns None
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.get("test:key:1")

    assert result is None
    mock_redis.get.assert_called_once_with("test:key:1")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_get_hit():
    """Test cache GET when key exists (cache hit).

    Scenario:
    - Redis returns cached JSON value
    - Expected: Cached value returned
    """
    from app.services.cache_service import CacheService
    import json

    # Mock Redis connection
    mock_redis = AsyncMock()
    cached_value = json.dumps({"id": 1, "title": "Task 1"})
    mock_redis.get = AsyncMock(return_value=cached_value)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.get("task:1")

    assert result == {"id": 1, "title": "Task 1"}
    mock_redis.get.assert_called_once_with("task:1")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_set_with_ttl():
    """Test cache SET with TTL (time-to-live).

    Scenario:
    - Set a cache value with 300 second TTL
    - Expected: Redis setex() called with correct TTL
    """
    from app.services.cache_service import CacheService
    import json

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    value = {"id": 1, "title": "Task 1"}
    result = await cache_svc.set("task:1", value, ttl=300)

    assert result is True
    mock_redis.setex.assert_called_once()
    call_args = mock_redis.setex.call_args
    assert call_args[0][0] == "task:1"  # Key
    assert call_args[0][1] == 300  # TTL


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_delete_on_update():
    """Test cache invalidation (delete) when data is updated.

    Scenario:
    - Delete cache key
    - Expected: Redis delete() called
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock(return_value=1)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.delete("task:1")

    assert result is True
    mock_redis.delete.assert_called_once_with("task:1")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_delete_pattern():
    """Test cache pattern deletion (e.g., all task:* keys).

    Scenario:
    - Delete all keys matching pattern
    - Expected: Redis scan + delete called for matching keys
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.scan = AsyncMock(return_value=(0, ["task:1", "task:2", "task:3"]))
    mock_redis.delete = AsyncMock(return_value=3)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.delete_pattern("task:*")

    assert result == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_set_with_default_ttl():
    """Test cache SET uses default TTL of 300s when not specified.

    Scenario:
    - Set cache value without specifying TTL
    - Expected: Default TTL of 300 used
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    value = {"id": 1}
    await cache_svc.set("task:1", value)  # No TTL specified

    call_args = mock_redis.setex.call_args
    # Default TTL should be 300
    assert call_args[0][1] == 300


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_health_check():
    """Test Redis connection health check.

    Scenario:
    - Check if Redis is reachable
    - Expected: Returns True if healthy
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.health_check()

    assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_get_handles_redis_error():
    """Test cache GET handles Redis connection errors gracefully.

    Scenario:
    - Redis throws connection error
    - Expected: Returns None instead of raising
    """
    from app.services.cache_service import CacheService

    # Mock Redis to raise error
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=Exception("Redis connection error"))

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.get("task:1")

    # Should return None on error
    assert result is None
    """Test cache GET when key doesn't exist (cache miss).
    
    Scenario:
    - Redis returns None (key not found)
    - Expected: Cache miss returns None
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.get("test:key:1")

    assert result is None
    mock_redis.get.assert_called_once_with("test:key:1")


@pytest.mark.unit
async def test_cache_get_hit():
    """Test cache GET when key exists (cache hit).

    Scenario:
    - Redis returns cached JSON value
    - Expected: Cached value returned
    """
    from app.services.cache_service import CacheService
    import json

    # Mock Redis connection
    mock_redis = AsyncMock()
    cached_value = json.dumps({"id": 1, "title": "Task 1"})
    mock_redis.get = AsyncMock(return_value=cached_value)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.get("task:1")

    assert result == {"id": 1, "title": "Task 1"}
    mock_redis.get.assert_called_once_with("task:1")


@pytest.mark.unit
async def test_cache_set_with_ttl():
    """Test cache SET with TTL (time-to-live).

    Scenario:
    - Set a cache value with 300 second TTL
    - Expected: Redis setex() called with correct TTL
    """
    from app.services.cache_service import CacheService
    import json

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    value = {"id": 1, "title": "Task 1"}
    result = await cache_svc.set("task:1", value, ttl=300)

    assert result is True
    mock_redis.setex.assert_called_once()
    call_args = mock_redis.setex.call_args
    assert call_args[0][0] == "task:1"  # Key
    assert call_args[0][1] == 300  # TTL


@pytest.mark.unit
async def test_cache_delete_on_update():
    """Test cache invalidation (delete) when data is updated.

    Scenario:
    - Delete cache key
    - Expected: Redis delete() called
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock(return_value=1)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.delete("task:1")

    assert result is True
    mock_redis.delete.assert_called_once_with("task:1")


@pytest.mark.unit
async def test_cache_delete_pattern():
    """Test cache pattern deletion (e.g., all task:* keys).

    Scenario:
    - Delete all keys matching pattern
    - Expected: Redis scan + delete called for matching keys
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.scan = AsyncMock(return_value=(0, ["task:1", "task:2", "task:3"]))
    mock_redis.delete = AsyncMock(return_value=3)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.delete_pattern("task:*")

    assert result == 3


@pytest.mark.unit
async def test_cache_set_with_default_ttl():
    """Test cache SET uses default TTL of 300s when not specified.

    Scenario:
    - Set cache value without specifying TTL
    - Expected: Default TTL of 300 used
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    value = {"id": 1}
    await cache_svc.set("task:1", value)  # No TTL specified

    call_args = mock_redis.setex.call_args
    # Default TTL should be 300
    assert call_args[0][1] == 300


@pytest.mark.unit
async def test_cache_health_check():
    """Test Redis connection health check.

    Scenario:
    - Check if Redis is reachable
    - Expected: Returns True if healthy
    """
    from app.services.cache_service import CacheService

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.health_check()

    assert result is True


@pytest.mark.unit
async def test_cache_get_handles_redis_error():
    """Test cache GET handles Redis connection errors gracefully.

    Scenario:
    - Redis throws connection error
    - Expected: Returns None instead of raising
    """
    from app.services.cache_service import CacheService

    # Mock Redis to raise error
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=Exception("Redis connection error"))

    cache_svc = CacheService("redis://localhost")
    cache_svc._redis = mock_redis

    result = await cache_svc.get("task:1")

    # Should return None on error
    assert result is None
