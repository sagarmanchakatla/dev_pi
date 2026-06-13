from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware
from app.api.v1 import health

logger = get_logger(__name__)

def create_app() -> FastAPI:
    # Setup logging first
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade SaaS API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Add middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Routers
    app.include_router(health.router, tags=["health"])

    @app.on_event("startup")
    async def on_startup():
        logger.info(
            "application_starting",
            app=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            debug=settings.DEBUG,
            database="configured" if settings.DATABASE_URL else "not configured",
            redis="configured" if settings.REDIS_URL else "not configured",
        )

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info(
            "application_stopping",
            app=settings.APP_NAME,
        )

    return app

app = create_app()
