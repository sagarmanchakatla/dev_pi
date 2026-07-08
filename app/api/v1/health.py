from fastapi import APIRouter
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/health/live")
async def liveness():
    """Liveness check — is the process alive?"""
    return {
        "status": "alive",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@router.get("/health/ready")
async def readiness():
    """Readiness check — is the app ready to serve traffic?"""
    checks = {}
    ready = True

    # Database check
    if settings.DATABASE_URL:
        try:
            from app.db.session import engine
            if engine:
                async with engine.connect() as conn:
                    await conn.execute(__import__('sqlalchemy').text("SELECT 1"))
                checks["database"] = "connected"
            else:
                checks["database"] = "not configured"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
            ready = False
    else:
        checks["database"] = "not configured"

    # Redis check
    if settings.REDIS_URL:
        try:
            from app.core.redis import get_redis
            r = await get_redis()
            await r.ping()
            checks["redis"] = "connected"
        except Exception as e:
            checks["redis"] = f"error: {str(e)}"
            ready = False
    else:
        checks["redis"] = "not configured"

    status_code = 200 if ready else 503
    return {
        "status": "ready" if ready else "not ready",
        "checks": checks
    }
