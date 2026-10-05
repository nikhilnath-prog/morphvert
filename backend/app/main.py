"""
Main FastAPI application entry point.

Sets up the application with:
- CORS middleware
- Security middleware
- Logging
- API routes
- Error handlers
- Lifespan events
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api.v1.endpoints import ai_pdf, conversions_public, download, files, pdf
from app.core.config import settings
from app.middleware.middleware import ErrorHandlingMiddleware, LoggingMiddleware, SecurityHeadersMiddleware
from app.utils.file_utils import ensure_upload_directories

import app.logging.logging_config  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    print("🚀 Starting Morphvert API...")
    ensure_upload_directories()
    print("✅ Storage directories ready")
    yield
    print("🛑 Shutting down Morphvert API...")
    print("✅ Shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "healthy", "version": settings.PROJECT_VERSION}


@app.get("/", tags=["root"])
async def root() -> dict:
    return {
        "message": "Welcome to Morphvert API",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


app.include_router(files.router, prefix=settings.API_V1_STR)
app.include_router(download.router, prefix=settings.API_V1_STR)
app.include_router(pdf.router, prefix=settings.API_V1_STR)
app.include_router(pdf.pdf_router, prefix=settings.API_V1_STR)
app.include_router(ai_pdf.router)
app.include_router(conversions_public.router, prefix=settings.API_V1_STR)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.PROJECT_DESCRIPTION,
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
