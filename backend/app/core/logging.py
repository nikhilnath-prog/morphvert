"""
Logging configuration for FastAPI application.

Sets up:
- Console logging with colors
- File logging
- Request/response logging
- Error logging with stack traces
"""

import logging
import logging.config
import os
import sys
from pathlib import Path

from app.core.config import settings


LOGS_DIR = Path(__file__).parent.parent.parent / "logs"


def _is_railway_deployment() -> bool:
    return bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_SERVICE_ID")
    )


ENABLE_FILE_LOGGING = not _is_railway_deployment()

if ENABLE_FILE_LOGGING:
    LOGS_DIR.mkdir(exist_ok=True)


# Custom UTF-8 compatible StreamHandler for Windows
class UTF8StreamHandler(logging.StreamHandler):
    """StreamHandler with UTF-8 encoding support for Windows."""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            # Encode to UTF-8 to handle Unicode characters
            stream = self.stream
            if hasattr(stream, 'buffer'):
                # If we have a buffer (like sys.stdout on Python 3), write to it with UTF-8
                stream.buffer.write((msg + self.terminator).encode('utf-8'))
            else:
                # Fallback for other streams
                stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


# Logging configuration dictionary
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },
    "handlers": {
        # Console handler (for terminal output) - UTF-8 compatible for Windows
        "console": {
            "class": "app.core.logging.UTF8StreamHandler",
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # Root logger
        "": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["console"],
        },
        # FastAPI/Starlette loggers
        "fastapi": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "starlette": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        # Suppress watchfiles DEBUG spam (file watcher)
        "watchfiles": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        # Suppress passlib DEBUG spam
        "passlib": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        # Application loggers
        "app": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "app.middleware": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "app.services": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "app.repositories": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "app.api": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

if ENABLE_FILE_LOGGING:
    LOGGING_CONFIG["handlers"]["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "level": "DEBUG",
        "formatter": "detailed",
        "filename": str(LOGS_DIR / "morphvert.log"),
        "maxBytes": 10485760,  # 10MB
        "backupCount": 5,
    }
    LOGGING_CONFIG["handlers"]["error_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "level": "ERROR",
        "formatter": "detailed",
        "filename": str(LOGS_DIR / "morphvert_errors.log"),
        "maxBytes": 10485760,  # 10MB
        "backupCount": 5,
    }
    LOGGING_CONFIG["loggers"][""]["handlers"] = ["console", "file", "error_file"]
    LOGGING_CONFIG["loggers"]["fastapi"]["handlers"] = ["console", "file"]
    LOGGING_CONFIG["loggers"]["starlette"]["handlers"] = ["console", "file"]
    LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"] = ["console", "file"]
    LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"] = ["console", "file"]
    LOGGING_CONFIG["loggers"]["watchfiles"]["handlers"] = ["file"]
    LOGGING_CONFIG["loggers"]["passlib"]["handlers"] = ["file"]
    LOGGING_CONFIG["loggers"]["app"]["handlers"] = ["console", "file", "error_file"]
    LOGGING_CONFIG["loggers"]["app.middleware"]["handlers"] = ["console", "file"]
    LOGGING_CONFIG["loggers"]["app.services"]["handlers"] = ["console", "file", "error_file"]
    LOGGING_CONFIG["loggers"]["app.repositories"]["handlers"] = ["console", "file"]
    LOGGING_CONFIG["loggers"]["app.api"]["handlers"] = ["console", "file", "error_file"]


def setup_logging() -> None:
    """
    Setup logging configuration.
    
    Call this once at application startup.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log startup info (no emojis for Windows compatibility)
    logger = logging.getLogger(__name__)
    logger.info("Logging configured (DEBUG={})".format(settings.DEBUG))
    logger.info("Logs directory: {}".format(LOGS_DIR))


# Module-level logger for this file
logger = logging.getLogger(__name__)
