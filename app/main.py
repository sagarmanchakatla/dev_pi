from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import health

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade SaaS API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    app.include_router(health.router, tags=["health"])

    @app.on_event("startup")
    async def on_startup():
        print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"Debug: {settings.DEBUG}")
        print(f"Database: {'configured' if settings.DATABASE_URL else 'not configured'}")
        print(f"Redis: {'configured' if settings.REDIS_URL else 'not configured'}")
        # SECRET_KEY is never logged

    @app.on_event("shutdown")
    async def on_shutdown():
        print(f"Shutting down {settings.APP_NAME}")

    return app

app = create_app()
