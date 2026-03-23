"""
Production Monitoring Setup with Prometheus & Grafana
Adds metrics collection endpoints for production observability
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from functools import wraps
from typing import Callable

# Define metrics
REQUEST_COUNT = Counter(
    'gts_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'gts_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'gts_active_requests',
    'Number of active requests'
)

BOT_EXECUTIONS = Counter(
    'gts_bot_executions_total',
    'Total bot executions',
    ['bot_name', 'status']
)

BOT_DURATION = Histogram(
    'gts_bot_execution_duration_seconds',
    'Bot execution duration',
    ['bot_name']
)

DATABASE_CONNECTIONS = Gauge(
    'gts_database_connections_active',
    'Active database connections'
)

WEBSOCKET_CONNECTIONS = Gauge(
    'gts_websocket_connections',
    'Active WebSocket connections'
)

CACHE_HITS = Counter(
    'gts_cache_hits_total',
    'Cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'gts_cache_misses_total',
    'Cache misses',
    ['cache_type']
)


def track_request_metrics(func: Callable) -> Callable:
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        
        try:
            response = await func(*args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
            
            # Record metrics
            REQUEST_COUNT.labels(
                method='GET',  # Would need to extract from request
                endpoint=func.__name__,
                status=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method='GET',
                endpoint=func.__name__
            ).observe(time.time() - start_time)
            
            return response
            
        finally:
            ACTIVE_REQUESTS.dec()
    
    return wrapper


def track_bot_execution(bot_name: str, success: bool, duration: float):
    """Track bot execution metrics"""
    BOT_EXECUTIONS.labels(
        bot_name=bot_name,
        status='success' if success else 'failure'
    ).inc()
    
    BOT_DURATION.labels(bot_name=bot_name).observe(duration)


def metrics_endpoint():
    """FastAPI endpoint to expose Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Usage example for FastAPI:
# from backend.monitoring.prometheus import metrics_endpoint, track_request_metrics
#
# @app.get("/metrics")
# async def get_metrics():
#     return metrics_endpoint()
#
# @app.get("/api/v1/bots")
# @track_request_metrics
# async def list_bots():
#     ...
