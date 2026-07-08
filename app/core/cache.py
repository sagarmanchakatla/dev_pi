import json
import functools
from typing import Optional, Callable, Any
from app.core.redis import get_redis
from app.core.logging import get_logger

logger = get_logger(__name__)

async def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache. Returns None on miss or error."""
    try:
        r = await get_redis()
        value = await r.get(key)
        if value:
            logger.info("cache_hit", key=key)
            return json.loads(value)
        logger.info("cache_miss", key=key)
        return None
    except Exception as e:
        logger.error("cache_get_error", key=key, error=str(e))
        return None

async def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Set a value in cache with TTL. Returns False on error."""
    try:
        r = await get_redis()
        await r.setex(key, ttl, json.dumps(value))
        logger.info("cache_set", key=key, ttl=ttl)
        return True
    except Exception as e:
        logger.error("cache_set_error", key=key, error=str(e))
        return False

async def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    try:
        r = await get_redis()
        await r.delete(key)
        logger.info("cache_delete", key=key)
        return True
    except Exception as e:
        logger.error("cache_delete_error", key=key, error=str(e))
        return False

async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern. Returns count deleted."""
    try:
        r = await get_redis()
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)
        logger.info("cache_delete_pattern", pattern=pattern, count=len(keys))
        return len(keys)
    except Exception as e:
        logger.error("cache_delete_pattern_error", pattern=pattern, error=str(e))
        return 0
