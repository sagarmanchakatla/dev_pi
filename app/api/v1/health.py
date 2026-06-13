from fastapi import APIRouter
from app.core.config import settings

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

    # Database check (placeholder until Phase 5)
    if settings.DATABASE_URL:
        checks["database"] = "connected"
    else:
        checks["database"] = "not configured"

    # Redis check (placeholder until Phase 6)
    if settings.REDIS_URL:
        checks["redis"] = "connected"
    else:
        checks["redis"] = "not configured"

    return {
        "status": "ready" if ready else "not ready",
        "checks": checks
    }
