"""Cache key generators for consistent key naming"""


def task_list_cache_key(user_id: int, status: str = None, search: str = None, page: int = 1) -> str:
    """Generate cache key for task list"""
    parts = [f"tasks:u{user_id}"]
    
    if status:
        parts.append(f"s{status}")
    if search:
        parts.append(f"q{search}")
    
    parts.append(f"p{page}")
    
    return ":".join(parts)


def task_cache_key(task_id: int) -> str:
    """Generate cache key for single task"""
    return f"task:t{task_id}"


def user_cache_key(user_id: int) -> str:
    """Generate cache key for user"""
    return f"user:u{user_id}"


# Cache TTLs (in seconds)
TASK_LIST_CACHE_TTL = 300  # 5 minutes
TASK_CACHE_TTL = 600  # 10 minutes
USER_CACHE_TTL = 3600  # 1 hour
