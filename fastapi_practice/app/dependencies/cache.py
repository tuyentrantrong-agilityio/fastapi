"""Cache dependencies for dependency injection"""

from ..services.cache_service import get_cache_service


async def get_cache():
    """Get cache service for dependency injection"""
    return get_cache_service()
