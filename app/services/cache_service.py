"""Redis caching service for API responses.

Provides high-level caching interface with automatic TTL management.
"""

import json
import logging
from typing import Any, Optional

from redis.asyncio import Redis, from_url

logger = logging.getLogger(__name__)


class CacheService:
    """Service to manage Redis cache operations"""

    def __init__(self, redis_url: str):
        """Initialize Redis connection"""
        self.redis_url = redis_url
        self._redis: Optional[Redis] = None

    @property
    async def redis(self) -> Redis:
        """Get or create Redis connection"""
        if self._redis is None:
            self._redis = from_url(self.redis_url, encoding="utf8", decode_responses=True)
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            redis = await self.redis
            value = await redis.get(key)

            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)

            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as exc:
            logger.warning(f"Cache GET error for {key}: {exc}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (in seconds)"""
        try:
            redis = await self.redis
            await redis.setex(key, ttl, json.dumps(value))
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as exc:
            logger.warning(f"Cache SET error for {key}: {exc}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            redis = await self.redis
            result = await redis.delete(key)
            if result:
                logger.debug(f"Cache DELETE: {key}")
            return bool(result)
        except Exception as exc:
            logger.warning(f"Cache DELETE error for {key}: {exc}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            redis = await self.redis
            cursor = 0
            count = 0

            while True:
                cursor, keys = await redis.scan(cursor, match=pattern)
                if keys:
                    count += await redis.delete(*keys)

                if cursor == 0:
                    break

            if count > 0:
                logger.debug(f"Cache FLUSH: {count} keys matching pattern '{pattern}'")

            return count
        except Exception as exc:
            logger.warning(f"Cache DELETE PATTERN error for {pattern}: {exc}")
            return 0

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            logger.info("Cache connection closed")

    async def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            redis = await self.redis
            await redis.ping()
            logger.debug("Cache health check: OK")
            return True
        except Exception as exc:
            logger.error(f"Cache health check failed: {exc}")
            return False


# Global cache instance
_cache_service: Optional[CacheService] = None


def get_cache_service(redis_url: str = None) -> CacheService:
    """Get or create global cache service"""
    global _cache_service

    if _cache_service is None:
        from ..core.config import settings

        redis_url = redis_url or settings.REDIS_URL
        _cache_service = CacheService(redis_url)

    return _cache_service
