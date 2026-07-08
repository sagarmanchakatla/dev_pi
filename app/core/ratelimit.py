import time
from fastapi import Request, HTTPException
from app.core.redis import get_redis
from app.core.logging import get_logger

logger = get_logger(__name__)

async def check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int, int]:
    """
    Sliding window rate limit check.
    Returns (is_limited, current_count, reset_at)
    """
    r = await get_redis()
    now = time.time()
    window_start = now - window_seconds
    reset_at = int(now) + window_seconds

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zcard(key)
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, window_seconds + 1)
    results = await pipe.execute()

    current_count = results[1]
    is_limited = current_count >= limit

    if is_limited:
        logger.warning(
            "rate_limit_exceeded",
            key=key,
            limit=limit,
            current=current_count,
        )

    return is_limited, current_count, reset_at


async def rate_limit_ip(
    request: Request,
    limit: int = 60,
    window_seconds: int = 60,
):
    """Rate limit by IP address. Use as a FastAPI dependency."""
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate:ip:{client_ip}"

    is_limited, count, reset_at = await check_rate_limit(
        key, limit, window_seconds
    )

    # Always add headers to response
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(max(0, limit - count - 1)),
        "X-RateLimit-Reset": str(reset_at),
    }

    if is_limited:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"Too many requests. Limit: {limit} per {window_seconds}s",
                "retry_after": window_seconds,
            },
            headers={
                "Retry-After": str(window_seconds),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_at),
            }
        )
