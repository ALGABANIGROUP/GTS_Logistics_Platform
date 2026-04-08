"""
Sentry Integration for Error Tracking and Monitoring
Implements real-time error tracking and performance monitoring
"""
import os
import logging
from typing import Optional

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
except ImportError:  # pragma: no cover
    sentry_sdk = None  # type: ignore[assignment]
    FastApiIntegration = None  # type: ignore[assignment]
    SqlalchemyIntegration = None  # type: ignore[assignment]
    LoggingIntegration = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def init_sentry(
    dsn: Optional[str] = None,
    environment: str = "development",
    traces_sample_rate: float = 0.1,
    enable: bool = True
):
    """
    Initialize Sentry for error tracking and performance monitoring
    
    Args:
        dsn: Sentry DSN (Data Source Name)
        environment: Environment name (development, staging, production)
        traces_sample_rate: Percentage of transactions to trace (0.0 to 1.0)
        enable: Whether to enable Sentry
    """
    if not enable:
        logger.info("Sentry integration disabled")
        return False
    
    if not dsn:
        logger.warning("Sentry DSN not configured - error tracking disabled")
        return False

    if sentry_sdk is None:
        logger.info("Sentry SDK not installed - integration disabled")
        return False
    
    try:
        # Configure Sentry SDK
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            
            # Integrations
            integrations=[
                # FastAPI integration
                FastApiIntegration(
                    transaction_style="endpoint",  # Group by endpoint
                    failed_request_status_codes=[400, 401, 403, 404, 405, 500, 502, 503],
                ),
                
                # SQLAlchemy integration
                SqlalchemyIntegration(),
                
                # Logging integration
                LoggingIntegration(
                    level=logging.INFO,        # Capture info and above
                    event_level=logging.ERROR  # Send errors as events
                ),
            ],
            
            # Performance Monitoring
            traces_sample_rate=traces_sample_rate,  # % of transactions to trace
            
            # Release tracking
            release=os.getenv("GIT_COMMIT", "unknown"),
            
            # Error filtering
            ignore_errors=[
                KeyboardInterrupt,
                "HTTPException",  # Don't send expected HTTP errors
            ],
            
            # Additional options
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send personally identifiable information
            max_breadcrumbs=50,
            debug=False,  # Set to True for debugging Sentry itself
            
            # Before send hook to filter/modify events
            before_send=before_send_hook,
        )
        
        logger.info(f"✅ Sentry initialized successfully (environment: {environment}, sample rate: {traces_sample_rate})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def before_send_hook(event, hint):
    """
    Filter or modify events before sending to Sentry
    Use this to:
    - Filter out sensitive data
    - Add custom context
    - Skip certain types of errors
    """
    # Skip health check errors
    if "request" in event and event["request"].get("url", "").endswith("/health"):
        return None
    
    # Filter sensitive headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[Filtered]"
    
    # Add custom tags
    event.setdefault("tags", {})
    event["tags"]["platform"] = "gts-logistics"
    
    return event


def capture_exception(exception: Exception, extra_context: dict = None):
    """
    Manually capture an exception and send to Sentry
    
    Args:
        exception: Exception to capture
        extra_context: Additional context to attach
    """
    if sentry_sdk is None:
        return
    if extra_context:
        with sentry_sdk.push_scope() as scope:
            for key, value in extra_context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_exception(exception)
    else:
        sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info", extra_context: dict = None):
    """
    Send a custom message to Sentry
    
    Args:
        message: Message to send
        level: Severity level (debug, info, warning, error, fatal)
        extra_context: Additional context
    """
    if sentry_sdk is None:
        return
    if extra_context:
        with sentry_sdk.push_scope() as scope:
            for key, value in extra_context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str = None, email: str = None, username: str = None):
    """
    Set user context for error tracking
    
    Args:
        user_id: User ID
        email: User email (will be filtered if send_default_pii=False)
        username: Username
    """
    if sentry_sdk is None:
        return
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username,
    })


def set_custom_context(context_name: str, context_data: dict):
    """
    Add custom context to Sentry events

    Args:
        context_name: Name of context section
        context_data: Dictionary of context data
    """
    if sentry_sdk is None:
        return
    sentry_sdk.set_context(context_name, context_data)


class SentryIntegration:
    """Sentry.io integration for error tracking"""

    def __init__(self):
        self.dsn = os.getenv('SENTRY_DSN')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.release_version = os.getenv('RELEASE_VERSION', '1.0.0')
        self.initialized = False
        self.client = sentry_sdk

    def initialize(self):
        """Initialize Sentry client"""
        if not self.dsn:
            logger.info("Sentry integration disabled - no DSN configured")
            return False

        success = init_sentry(
            dsn=self.dsn,
            environment=self.environment,
            traces_sample_rate=0.1 if self.environment == 'production' else 1.0
        )

        if success:
            self.initialized = True

        return success

    def capture_exception(self, error: Exception, context: Optional[dict] = None):
        """Capture exception to Sentry"""
        capture_exception(error, context)

    def capture_message(self, message: str, level: str = "info", context: Optional[dict] = None):
        """Capture message to Sentry"""
        capture_message(message, level, context)

    def is_enabled(self) -> bool:
        """Check if Sentry is enabled and initialized"""
        return self.initialized and self.dsn is not None


def set_tag(key: str, value: str):
    """
    Add a custom tag to Sentry events
    Tags are searchable in Sentry UI
    
    Args:
        key: Tag key
        value: Tag value
    """
    if sentry_sdk is None:
        return
    sentry_sdk.set_tag(key, value)


def start_transaction(name: str, op: str = "function"):
    """
    Start a performance monitoring transaction
    
    Args:
        name: Transaction name
        op: Operation type (http, db, function, etc.)
    
    Returns:
        Transaction object (use as context manager)
    
    Example:
        with start_transaction("process_shipment", "function"):
            # Your code here
            pass
    """
    if sentry_sdk is None:
        class _NullTransaction:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        return _NullTransaction()
    return sentry_sdk.start_transaction(name=name, op=op)


# Example usage in FastAPI endpoints
"""
from backend.monitoring.sentry_integration import capture_exception, set_user_context, start_transaction

@router.get("/example")
async def example_endpoint(current_user: dict = Depends(get_current_user)):
    # Set user context
    set_user_context(
        user_id=str(current_user["id"]),
        username=current_user.get("username")
    )
    
    # Start performance tracking
    with start_transaction("example_endpoint", "http"):
        try:
            # Your code here
            result = process_data()
            return result
        except Exception as e:
            # Manually capture specific exceptions with context
            capture_exception(e, extra_context={
                "operation": "example_endpoint",
                "user_id": current_user["id"]
            })
            raise
"""
