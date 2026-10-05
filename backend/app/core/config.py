"""
Configuration management for Morphvert backend.

Handles all environment variables, settings, and configuration management.
Supports multiple environments (development, testing, production).
"""

from pathlib import Path
from typing import List, Optional, Union
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # === PROJECT INFO ===
    PROJECT_NAME: str = "Morphvert API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Advanced File Conversion Platform"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|testing|production)$")
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # === DATABASE ===
    DATABASE_URL: Optional[str] = None
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # === REDIS ===
    REDIS_URL: Optional[str] = None
    REDIS_CELERY_URL: Optional[str] = None

    # === JWT & SECURITY ===
    SECRET_KEY: str
    GEMINI_API_KEY: Optional[str] = None  # Optional; required only for AI PDF summarization
    GEMINI_MODEL: str = "gemini-3.8-flash"  # Override in backend/.env if needed
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_AUDIENCE: str = "morphvert-api"

    # === AWS S3 ===
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None

    # === STORAGE ===
    LOCAL_STORAGE_PATH: str = "../uploads"
    CONVERTED_FILES_PATH: str = "../converted"
    TEMP_FILES_PATH: str = "../temp"
    LOGS_DIR: str = "../logs"
    MAX_FILE_SIZE: int = 52428800  # 50 MB
    FILE_RETENTION_DAYS: int = 30

    # === FEATURES ===
    ENABLE_OCR: bool = True
    ENABLE_AI_SUMMARY: bool = True
    ENABLE_BATCH_PROCESSING: bool = True
    MAX_BATCH_SIZE: int = 100

    # === CELERY ===
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_TIME_LIMIT: int = 3600
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3000

    # === CORS ===
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "https://morphvert.vercel.app"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: Union[str, List[str]] = ["*"]
    CORS_ALLOW_HEADERS: Union[str, List[str]] = ["*"]

    # === API ===
    API_V1_STR: str = "/api/v1"

    # === ADMIN ===
    FIRST_SUPERUSER_EMAIL: str = "admin@morphvert.com"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"

    class Config:
        """Pydantic config."""
        # Always load backend/.env, even if Uvicorn is launched from another directory.
        env_file = Path(__file__).resolve().parents[2] / ".env"
        case_sensitive = True
        extra = "ignore"

    @validator("DATABASE_URL", pre=True, always=True)
    def default_database_url(cls, v: str) -> str:
        """Fallback to SQLite when Railway does not provide DATABASE_URL and validate supplied URLs."""
        raw_value = str(v or "").strip()
        if raw_value:
            if not raw_value.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite+aiosqlite://")):
                raise ValueError("DATABASE_URL must be a PostgreSQL or SQLite connection string")
            return raw_value

        project_root = Path(__file__).resolve().parents[2]
        fallback_db = project_root / "morphvert.db"
        return f"sqlite+aiosqlite:///{fallback_db}"

    @staticmethod
    def _resolve_storage_path(value: str) -> str:
        """Resolve storage paths inside the backend project root."""
        raw_value = str(value).strip()
        path = Path(raw_value).expanduser()
        project_root = Path(__file__).resolve().parents[2]
        storage_names = {"uploads", "converted", "temp", "logs"}

        if path.is_absolute():
            if len(path.parts) == 2 and path.name in storage_names:
                return str((project_root / path.name).resolve())
            return str(path.resolve())

        normalized = raw_value.replace("\\", "/")
        if normalized.startswith("/"):
            stripped_parts = [part for part in normalized.split("/") if part]
            if len(stripped_parts) == 1 and stripped_parts[0] in storage_names:
                return str((project_root / stripped_parts[0]).resolve())
            return str(path.resolve())

        return str((project_root / path).resolve())

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: any) -> List[str]:
        """Parse CORS origins from JSON list or comma-separated string."""
        if isinstance(v, str):
            value = v.strip()
            if value.startswith("["):
                import json

                return json.loads(value)

            return [origin.strip() for origin in value.split(",") if origin.strip()]

        return v

    @validator("CORS_ORIGINS")
    def normalize_cors_origins(cls, v: List[str]) -> List[str]:
        """Ensure CORS origins are always returned as a list of non-empty strings."""
        return [origin.strip() for origin in v if origin and origin.strip()]

    @validator("CORS_ALLOW_METHODS", "CORS_ALLOW_HEADERS", pre=True)
    def assemble_cors_allow_lists(cls, v: any) -> List[str]:
        """Parse CORS allow lists from JSON list or comma-separated string."""
        if isinstance(v, str):
            value = v.strip()
            if value.startswith("["):
                import json

                return json.loads(value)

            return [item.strip() for item in value.split(",") if item.strip()]

        return v

    @validator("CORS_ALLOW_METHODS", "CORS_ALLOW_HEADERS")
    def normalize_cors_allow_lists(cls, v: List[str]) -> List[str]:
        """Ensure CORS allow lists are always returned as cleaned lists."""
        return [item.strip() for item in v if item and item.strip()]

    @validator("LOCAL_STORAGE_PATH", "CONVERTED_FILES_PATH", "TEMP_FILES_PATH", "LOGS_DIR", pre=True)
    def anchor_storage_paths(cls, v: str) -> str:
        """Resolve relative storage paths against the backend project root."""
        return cls._resolve_storage_path(v)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses @lru_cache for performance - settings are loaded once and cached.
    Useful in production to avoid repeated environment variable reads.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Export settings for easy import
settings = get_settings()
