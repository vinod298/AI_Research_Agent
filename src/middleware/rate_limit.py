import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config.settings import settings
from src.core.exceptions import RateLimitExceededException
from src.core.redis import redis_manager


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed token bucket rate limiter middleware."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi") or request.url.path.startswith("/static"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        current_minute = int(time.time() // 60)
        rate_key = f"rate_limit:{client_ip}:{current_minute}"

        request_count = await redis_manager.incr(rate_key, ttl=60)
        if request_count > settings.RATE_LIMIT_PER_MINUTE:
            raise RateLimitExceededException()

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(max(0, settings.RATE_LIMIT_PER_MINUTE - request_count))
        return response
