"""
Logging configuration for Morphvert.

Sets up structured logging with proper levels and formatting.
"""

import logging
import logging.config
import os
from pathlib import Path

from app.core.config import settings

try:
    from pythonjsonlogger.jsonlogger import JsonFormatter
except ImportError:  # pragma: no cover - optional dependency
    JsonFormatter = None


# Create logs directory
log_dir = Path(settings.LOGS_DIR)


def _is_railway_deployment() -> bool:
    return bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_SERVICE_ID")
    )


ENABLE_FILE_LOGGING = not _is_railway_deployment()

if ENABLE_FILE_LOGGING:
    log_dir.mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": settings.LOG_LEVEL,
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
        },
        "app": {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

if ENABLE_FILE_LOGGING:
    LOGGING_CONFIG["handlers"]["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "detailed",
        "filename": f"{log_dir}/app.log",
        "maxBytes": 10485760,  # 10 MB
        "backupCount": 10,
        "level": settings.LOG_LEVEL,
    }
    LOGGING_CONFIG["handlers"]["error_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "detailed",
        "filename": f"{log_dir}/error.log",
        "maxBytes": 10485760,  # 10 MB
        "backupCount": 10,
        "level": "ERROR",
    }
    LOGGING_CONFIG["loggers"][""]["handlers"] = ["console", "file", "error_file"]
    LOGGING_CONFIG["loggers"]["app"]["handlers"] = ["console", "file", "error_file"]
    LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"] = ["console", "file"]

if JsonFormatter is not None:
    LOGGING_CONFIG["formatters"]["json"] = {
        "()": JsonFormatter,
        "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
    }
else:
    LOGGING_CONFIG["formatters"]["json"] = {
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
