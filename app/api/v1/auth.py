from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.core.security import (
    verify_password, hash_password,
    create_access_token, decode_token
)
from app.core.redis import get_redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Mock user store (replace with real DB in production)
MOCK_USERS_DB = {
    "alice@example.com": {
        "id": 1,
        "email": "alice@example.com",
        "hashed_password": hash_password("password123"),
        "role": "admin",
    },
    "bob@example.com": {
        "id": 2,
        "email": "bob@example.com",
        "hashed_password": hash_password("password456"),
        "role": "user",
    },
}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@router.post("/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT access token."""
    user = MOCK_USERS_DB.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        logger.warning(
            "login_failed",
            email=form_data.username,
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, jti = create_access_token(user["id"], user["role"])

    logger.info("login_success", user_id=user["id"], role=user["role"])

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.post("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Invalidate the current access token."""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = payload.get("jti")
    exp = payload.get("exp")

    if jti and exp:
        # Add to blacklist until token naturally expires
        import time
        ttl = int(exp - time.time())
        if ttl > 0:
            r = await get_redis()
            await r.setex(f"blacklist:{jti}", ttl, "1")
            logger.info("token_blacklisted", jti=jti, ttl=ttl)

    return {"message": "Successfully logged out"}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency that validates JWT and checks blacklist.
    Use this to protect endpoints that require authentication.
    """
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check blacklist
    jti = payload.get("jti")
    if jti:
        r = await get_redis()
        is_blacklisted = await r.exists(f"blacklist:{jti}")
        if is_blacklisted:
            logger.warning("blacklisted_token_used", jti=jti)
            raise HTTPException(
                status_code=401,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return {
        "user_id": int(payload["sub"]),
        "role": payload["role"],
        "jti": jti,
    }
