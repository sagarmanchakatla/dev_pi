import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis_client = None

async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        if not settings.REDIS_URL:
            raise RuntimeError("Redis not configured")
        _redis_client = redis.from_url(
            settings.REDIS_URL.get_secret_value(),
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client

async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
