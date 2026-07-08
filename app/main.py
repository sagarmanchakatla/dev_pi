from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware
from app.api.v1 import health
from app.api.v1 import users

logger = get_logger(__name__)

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade SaaS API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(health.router, tags=["health"])
    app.include_router(users.router, prefix="/api/v1", tags=["users"])

    @app.on_event("startup")
    async def on_startup():
        logger.info(
            "application_starting",
            app=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
        )

    @app.on_event("shutdown")
    async def on_shutdown():
        from app.core.redis import close_redis
        await close_redis()
        logger.info("application_stopping", app=settings.APP_NAME)

    return app

app = create_app()
