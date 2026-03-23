"""
Enhanced Logging Configuration for GTS Logistics Platform
Provides structured logging for operations, performance monitoring, and system events.
"""

import logging
import logging.handlers
import os
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, Optional, Set


class StructuredFormatter(logging.Formatter):
    """Custom formatter that adds structured data to log records."""

    def format(self, record: logging.LogRecord) -> str:
        # Add timestamp if not present
        if not hasattr(record, 'timestamp'):
            record.timestamp = datetime.now().isoformat()

        # Add structured data
        if hasattr(record, 'extra_data') and record.extra_data:
            structured_data = {
                'timestamp': record.timestamp,
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'extra_data': record.extra_data
            }
            return json.dumps(structured_data, default=str)
        else:
            # Standard format for regular logs
            return super().format(record)


def _resolve_log_level(name: Optional[str]) -> int:
    """Return a numeric log level, defaulting to INFO if the name is invalid."""
    if not name:
        return logging.INFO
    normalized = name.strip().upper()
    return getattr(logging, normalized, logging.INFO)


def _parse_output_targets(output: str) -> Set[str]:
    """Normalize the LOG_OUTPUT value into individual targets."""
    normalized = output.lower()
    for sep in ("+", ","):
        normalized = normalized.replace(sep, " ")
    return {token.strip() for token in normalized.split() if token.strip()}


def _get_formatter(format_name: str) -> logging.Formatter:
    """Return the formatter instance that matches the configured log format."""
    if format_name == "json":
        return StructuredFormatter()
    return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def setup_logging():
    """Setup comprehensive logging configuration for the GTS platform."""

    # Create logs directory
    logs_dir = Path(os.getenv("LOG_DIR", "logs"))
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    log_level = _resolve_log_level(
        os.getenv("GTS_LOG_LEVEL") or os.getenv("LOG_LEVEL") or "INFO"
    )
    root_logger.setLevel(log_level)

    log_format = os.getenv("LOG_FORMAT", "json").strip().lower()
    output_targets = _parse_output_targets(os.getenv("LOG_OUTPUT", "stdout"))
    console_formatter = _get_formatter(log_format)

    log_file_value = os.getenv("LOG_FILE_PATH", "").strip()
    log_file_path = (
        Path(log_file_value).expanduser()
        if log_file_value
        else logs_dir / "application.log"
    )
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    file_formatter = _get_formatter(log_format)

    if output_targets & {"stdout", "console", "all", "both"}:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    if output_targets & {"file", "all", "both"}:
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Operations logger - tracks all operation activities
    operations_logger = logging.getLogger("operation_tracking")
    operations_logger.setLevel(log_level)
    operations_logger.propagate = False  # Don't propagate to root

    # Rotating file handler for operations
    operations_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "operations.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    operations_handler.setLevel(log_level)
    operations_formatter = StructuredFormatter()
    operations_handler.setFormatter(operations_formatter)
    operations_logger.addHandler(operations_handler)

    # Performance logger - tracks performance metrics
    performance_logger = logging.getLogger("performance_monitoring")
    performance_logger.setLevel(log_level)
    performance_logger.propagate = False

    # Rotating file handler for performance
    performance_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "performance.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    performance_handler.setLevel(logging.INFO)
    performance_formatter = StructuredFormatter()
    performance_handler.setFormatter(performance_formatter)
    performance_logger.addHandler(performance_handler)

    # Security logger - tracks security events
    security_logger = logging.getLogger("security_events")
    security_logger.setLevel(max(log_level, logging.WARNING))
    security_logger.propagate = False

    security_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "security.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    security_handler.setLevel(max(log_level, logging.WARNING))
    security_formatter = StructuredFormatter()
    security_handler.setFormatter(security_formatter)
    security_logger.addHandler(security_handler)

    # API logger - tracks API requests and responses
    api_logger = logging.getLogger("api_requests")
    api_logger.setLevel(log_level)
    api_logger.propagate = False

    api_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "api.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    api_handler.setLevel(log_level)
    api_formatter = StructuredFormatter()
    api_handler.setFormatter(api_formatter)
    api_logger.addHandler(api_handler)

    # Error logger - tracks all errors and exceptions
    error_logger = logging.getLogger("error_tracking")
    error_logger.setLevel(max(log_level, logging.ERROR))
    error_logger.propagate = False

    error_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "errors.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(max(log_level, logging.ERROR))
    error_formatter = StructuredFormatter()
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)


def log_operation_event(operation_id: str, event_type: str, message: str, extra_data: Dict[str, Any] = None):
    """Log operation events with structured data."""
    logger = logging.getLogger("operation_tracking")
    logger.info(f"[{event_type}] {message}", extra={
        'operation_id': operation_id,
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        'extra_data': extra_data or {}
    })


def log_performance_metric(metric_name: str, value: float, operation_id: str = None, extra_data: Dict[str, Any] = None):
    """Log performance metrics."""
    logger = logging.getLogger("performance_monitoring")
    logger.info(f"[{metric_name}] Value: {value}", extra={
        'metric_name': metric_name,
        'value': value,
        'operation_id': operation_id,
        'timestamp': datetime.now().isoformat(),
        'extra_data': extra_data or {}
    })


def log_security_event(event_type: str, message: str, user_id: str = None, extra_data: Dict[str, Any] = None):
    """Log security events."""
    logger = logging.getLogger("security_events")
    logger.warning(f"[{event_type}] {message}", extra={
        'event_type': event_type,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        'extra_data': extra_data or {}
    })


def log_api_request(method: str, endpoint: str, status_code: int, duration: float, user_id: str = None):
    """Log API requests."""
    logger = logging.getLogger("api_requests")
    logger.info(f"{method} {endpoint} - {status_code} ({duration:.2f}s)", extra={
        'method': method,
        'endpoint': endpoint,
        'status_code': status_code,
        'duration': duration,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    })


def log_error(error_type: str, message: str, traceback: str = None, extra_data: Dict[str, Any] = None):
    """Log errors and exceptions."""
    logger = logging.getLogger("error_tracking")
    logger.error(f"[{error_type}] {message}", extra={
        'error_type': error_type,
        'message': message,
        'traceback': traceback,
        'timestamp': datetime.now().isoformat(),
        'extra_data': extra_data or {}
    })


# Initialize logging when module is imported
setup_logging()
