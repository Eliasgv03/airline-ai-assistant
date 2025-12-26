"""
Enhanced logging middleware for FastAPI

Logs all requests with detailed information for debugging.
"""

from collections.abc import Callable
import time
from typing import cast

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = f"{int(time.time() * 1000)}"

        # Log request
        logger.info(
            f"🔵 [{request_id}] {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Log headers (excluding sensitive data)
        if logger.level <= 10:  # DEBUG level
            headers = dict(request.headers)
            # Remove sensitive headers
            headers.pop("authorization", None)
            headers.pop("cookie", None)
            logger.debug(f"📋 [{request_id}] Headers: {headers}")

        # Process request
        start_time = time.time()

        try:
            response = await call_next(request)

            # Calculate duration
            duration = (time.time() - start_time) * 1000  # ms

            # Log response
            status_emoji = "✅" if response.status_code < 400 else "❌"
            logger.info(
                f"{status_emoji} [{request_id}] {request.method} {request.url.path} "
                f"→ {response.status_code} ({duration:.2f}ms)"
            )

            return cast(Response, response)

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"❌ [{request_id}] {request.method} {request.url.path} "
                f"→ ERROR ({duration:.2f}ms): {str(e)}",
                exc_info=True,
            )
            raise
