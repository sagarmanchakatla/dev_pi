from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class Base(DeclarativeBase):
    pass

def get_engine():
    if not settings.DATABASE_URL:
        return None

    db_url = settings.DATABASE_URL.get_secret_value()
    # Convert postgresql:// to postgresql+asyncpg://
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return create_async_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,   # verify connection before using
        echo=settings.DEBUG,  # log SQL in debug mode only
    )

engine = get_engine()

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
) if engine else None

async def get_db():
    if not AsyncSessionLocal:
        raise RuntimeError("Database not configured")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
