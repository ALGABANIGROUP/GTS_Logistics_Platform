"""
Enhanced structured logging system for GTS Logistics.
Provides JSON logging, request tracking, and security audit trails.
"""
from __future__ import annotations

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import os

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for better parsing and analysis."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
        
        return json.dumps(log_data, default=str)


class RequestLogger:
    """Log HTTP requests with security context."""
    
    @staticmethod
    def log_request(
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log HTTP request with metadata."""
        logger = logging.getLogger("gts.api.requests")
        
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        
        if status_code >= 500:
            logger.error(f"Request failed: {method} {path}", extra={"extra_data": log_data})
        elif status_code >= 400:
            logger.warning(f"Request error: {method} {path}", extra={"extra_data": log_data})
        else:
            logger.info(f"Request: {method} {path}", extra={"extra_data": log_data})


class SecurityLogger:
    """Log security-related events."""
    
    @staticmethod
    def log_auth_attempt(
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """Log authentication attempt."""
        logger = logging.getLogger("gts.security.auth")
        
        log_data = {
            "email": email,
            "success": success,
            "ip_address": ip_address,
            "reason": reason,
        }
        
        if success:
            logger.info(f"Authentication success: {email}", extra={"extra_data": log_data})
        else:
            logger.warning(f"Authentication failed: {email}", extra={"extra_data": log_data})
    
    @staticmethod
    def log_permission_denied(
        user_id: str,
        resource: str,
        action: str,
        required_role: Optional[str] = None
    ):
        """Log permission denied event."""
        logger = logging.getLogger("gts.security.authz")
        
        log_data = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "required_role": required_role,
        }
        
        logger.warning(f"Permission denied: {user_id} -> {action} on {resource}", 
                      extra={"extra_data": log_data})
    
    @staticmethod
    def log_suspicious_activity(
        user_id: Optional[str],
        activity_type: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log suspicious security activity."""
        logger = logging.getLogger("gts.security.alerts")
        
        log_data = {
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details,
            "ip_address": ip_address,
        }
        
        logger.error(f"Suspicious activity: {activity_type}", extra={"extra_data": log_data})


class BotLogger:
    """Log bot execution and automation events."""
    
    @staticmethod
    def log_bot_execution(
        bot_name: str,
        status: str,
        duration_ms: float,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Log bot execution."""
        logger = logging.getLogger("gts.bots.execution")
        
        log_data = {
            "bot_name": bot_name,
            "status": status,
            "duration_ms": duration_ms,
            "result": result,
            "error": error,
        }
        
        if status == "success":
            logger.info(f"Bot execution success: {bot_name}", extra={"extra_data": log_data})
        else:
            logger.error(f"Bot execution failed: {bot_name}", extra={"extra_data": log_data})


def setup_logging(
    app_name: str = "gts",
    log_level: str = "INFO",
    enable_json: bool = True,
    enable_file: bool = True
):
    """
    Setup application logging with JSON formatting and file handlers.
    
    Args:
        app_name: Application name for logger namespace
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Use JSON formatting
        enable_file: Enable file logging
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if enable_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file:
        # General application log
        app_handler = logging.FileHandler(LOGS_DIR / f"{app_name}.log")
        app_handler.setLevel(level)
        app_handler.setFormatter(JSONFormatter() if enable_json else console_handler.formatter)
        root_logger.addHandler(app_handler)
        
        # Error-only log
        error_handler = logging.FileHandler(LOGS_DIR / f"{app_name}_errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter() if enable_json else console_handler.formatter)
        root_logger.addHandler(error_handler)
        
        # Security audit log
        security_handler = logging.FileHandler(LOGS_DIR / "security_audit.log")
        security_handler.setLevel(logging.INFO)
        security_handler.setFormatter(JSONFormatter() if enable_json else console_handler.formatter)
        
        # Only security logs
        security_logger = logging.getLogger("gts.security")
        security_logger.addHandler(security_handler)
        security_logger.propagate = False  # Don't send to root logger
    
    # Silence noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    logging.info(f"✅ Logging initialized: level={log_level}, json={enable_json}, file={enable_file}")


# Convenience loggers
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the GTS namespace."""
    return logging.getLogger(f"gts.{name}")
