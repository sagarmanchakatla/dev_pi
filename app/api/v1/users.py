from fastapi import APIRouter
from app.core.cache import cache_get, cache_set, cache_delete
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Simulated user data (real DB queries come in Phase 5 integration)
MOCK_USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
}

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    cache_key = f"cache:user:{user_id}"

    # Try cache first
    cached = await cache_get(cache_key)
    if cached:
        cached["_source"] = "cache"
        return cached

    # Cache miss — get from "database"
    user = MOCK_USERS.get(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    # Store in cache for 5 minutes
    await cache_set(cache_key, user, ttl=300)

    user["_source"] = "database"
    return user

@router.delete("/users/{user_id}/cache")
async def invalidate_user_cache(user_id: int):
    """Manually invalidate a user's cache entry."""
    cache_key = f"cache:user:{user_id}"
    deleted = await cache_delete(cache_key)
    return {"invalidated": deleted, "key": cache_key}
