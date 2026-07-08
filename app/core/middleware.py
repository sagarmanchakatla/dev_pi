import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        request.state.request_id = request_id

        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error=str(e),
            )
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)

        logger.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id

        # Add rate limit headers if set by rate limiter
        if hasattr(request.state, "rate_limit_headers"):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value

        return response
