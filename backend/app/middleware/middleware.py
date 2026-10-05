"""
HTTP middleware for request/response processing.

Includes logging, error handling, CORS, and security headers.
"""

import time
import logging
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details.
        
        Includes:
        - Request method and path
        - Processing time
        - Response status code
        - Request ID for tracing
        """
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", str(time.time()))
        
        # Log request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] Completed {response.status_code} in {process_time:.3f}s",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time,
            },
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # CSP: Allow Swagger UI CDN resources and inline scripts for documentation
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' https: data:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://"
        )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors that might occur during request processing."""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(
                f"Unhandled exception: {exc}",
                exc_info=True,
                extra={
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            
            # Return error response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "status_code": 500,
                    "message": "Internal server error",
                    "detail": str(exc) if settings.DEBUG else None,
                },
            )
