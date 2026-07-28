import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        path = request.url.path
        method = request.method

        response = await call_next(request)

        process_time = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Process-Time-Ms"] = str(process_time)

        logger.info(f"{method} {path} - Status: {response.status_code} - Duration: {process_time}ms")
        return response
