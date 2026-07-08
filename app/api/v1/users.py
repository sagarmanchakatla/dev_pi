from fastapi import APIRouter, Depends, Request, HTTPException
from app.core.cache import cache_get, cache_set, cache_delete
from app.core.ratelimit import rate_limit_ip
from app.core.logging import get_logger
from app.api.v1.auth import get_current_user

logger = get_logger(__name__)
router = APIRouter()

MOCK_USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
}

# /users/me MUST come before /users/{user_id}
@router.get("/users/me")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get the authenticated user's profile. Requires valid JWT."""
    user_id = current_user["user_id"]
    user = MOCK_USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {**user, "authenticated_as": current_user["role"]}


@router.get(
    "/users/{user_id}",
    dependencies=[Depends(rate_limit_ip)]
)
async def get_user(user_id: int):
    cache_key = f"cache:user:{user_id}"

    cached = await cache_get(cache_key)
    if cached:
        cached["_source"] = "cache"
        return cached

    user = MOCK_USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await cache_set(cache_key, user, ttl=300)
    result = dict(user)
    result["_source"] = "database"
    return result


@router.delete("/users/{user_id}/cache")
async def invalidate_user_cache(user_id: int):
    cache_key = f"cache:user:{user_id}"
    deleted = await cache_delete(cache_key)
    return {"invalidated": deleted, "key": cache_key}