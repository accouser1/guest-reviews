"""Logging Configuration"""

import sys
import structlog
from typing import Any

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.LOG_LEVEL.upper(), structlog.stdlib.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


# Global logger instance
logger = structlog.get_logger()


def log_request(method: str, path: str, status_code: int, duration: float) -> None:
    """Log HTTP request"""
    logger.info(
        "http_request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
    )


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log error with context"""
    logger.error(
        "error_occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        **(context or {}),
        exc_info=True,
    )
