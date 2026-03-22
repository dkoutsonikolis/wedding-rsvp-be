import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from utils.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, duration, client IP (2xx–3xx INFO; 4xx–5xx WARNING)."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/ready"):
            return await call_next(request)

        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code
        if 200 <= status_code < 400:
            log_level = "INFO"
        else:
            log_level = "WARNING"

        log_message = (
            f"{request.method} {request.url.path} - "
            f"{status_code} - "
            f"{process_time:.2f}ms - "
            f"IP: {client_ip}"
        )

        if log_level == "INFO":
            logger.info(log_message)
        else:
            logger.warning(log_message)

        return response
