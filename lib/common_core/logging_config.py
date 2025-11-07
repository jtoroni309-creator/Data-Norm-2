"""
Standardized logging configuration for all microservices

Provides consistent logging format, levels, and handlers across all services.
"""

import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with additional fields

    Adds:
    - service_name: Name of the microservice
    - correlation_id: Request correlation ID (if available)
    """

    def __init__(self, *args, service_name: str = "unknown", **kwargs):
        super().__init__(*args, **kwargs)
        self.service_name = service_name

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Add service name
        log_record["service"] = self.service_name

        # Add extra fields if present
        if hasattr(record, "correlation_id"):
            log_record["correlation_id"] = record.correlation_id


def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    json_format: bool = False
) -> logging.Logger:
    """
    Configure logging for a microservice

    Args:
        service_name: Name of the service (e.g., "identity", "analytics")
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format for logs (useful for production)

    Returns:
        Configured logger instance

    Usage:
        from lib.common_core import setup_logging

        logger = setup_logging("identity", log_level="INFO", json_format=False)
        logger.info("Service started")
    """

    # Get logger
    logger = logging.getLogger(service_name)

    # Clear existing handlers
    logger.handlers.clear()

    # Set log level
    log_level_value = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(log_level_value)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_value)

    # Configure formatter
    if json_format:
        # JSON formatter for production
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            service_name=service_name,
            rename_fields={"levelname": "level", "asctime": "timestamp"}
        )
    else:
        # Human-readable formatter for development
        formatter = logging.Formatter(
            f"%(asctime)s - [{service_name}] - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    logger.info(
        f"Logging configured for {service_name} | "
        f"Level: {log_level} | "
        f"JSON format: {json_format}"
    )

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module

    Args:
        name: Module name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter with correlation ID support

    Usage:
        logger = logging.getLogger(__name__)
        adapter = LoggerAdapter(logger, {"correlation_id": "abc123"})
        adapter.info("Processing request")
    """

    def process(self, msg, kwargs):
        """Add extra fields to log records"""
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
