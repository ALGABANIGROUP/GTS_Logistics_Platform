"""
Geo-Restriction Middleware & IP Verification
Handles geographic restrictions for features like Load Board (US/CA only)
"""

import logging
from fastapi import Request, HTTPException, status
from functools import wraps
try:
    import requests
except ImportError:
    requests = None  # type: ignore
from typing import Optional, List

logger = logging.getLogger(__name__)


class GeoRestrictionService:
    """Geographic access control service for features"""
    
    # Default allowed countries for Load Board
    LOAD_BOARD_ALLOWED_COUNTRIES = ['US', 'CA']
    
    # GeoIP service (you can use ipapi.co, ip-api.com, or MaxMind)
    GEO_IP_API = "http://ip-api.com/json/{ip}"
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Get the real client IP address"""
        # Check for proxies/load balancers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if request.client:
            return request.client.host
        return "127.0.0.1"
    
    @staticmethod
    def get_country_from_ip(ip_address: str) -> Optional[str]:
        """Get country code from IP address"""
        if requests is None:
            logger.warning("requests library not available")
            return None
        
        try:
            # Skip local IPs
            if ip_address in ['127.0.0.1', 'localhost', '::1']:
                logger.info(f"Local IP detected: {ip_address}, defaulting to US")
                return 'US'  # Default for development
            
            # Call GeoIP API
            response = requests.get(
                GeoRestrictionService.GEO_IP_API.format(ip=ip_address),
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                country_code = data.get('countryCode', 'UNKNOWN')
                logger.info(f"IP {ip_address} -> Country: {country_code}")
                return country_code
            else:
                logger.warning(f"GeoIP API failed for {ip_address}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting country for IP {ip_address}: {e}")
            return None
    
    @staticmethod
    def is_ip_allowed_for_load_board(ip_address: str) -> bool:
        """Validate whether an IP is allowed to access Load Board."""
        country = GeoRestrictionService.get_country_from_ip(ip_address)
        
        if not country:
            # If we can't determine country, allow but log
            logger.warning(f"Could not determine country for IP {ip_address}, allowing access")
            return True
        
        is_allowed = country in GeoRestrictionService.LOAD_BOARD_ALLOWED_COUNTRIES
        
        if not is_allowed:
            logger.info(f"Load Board access denied for IP {ip_address} from {country}")
        
        return is_allowed
    
    @staticmethod
    def check_geo_restriction(request: Request, feature_name: str, allowed_countries: List[str]) -> bool:
        """Validate feature access based on detected country and allowlist."""
        client_ip = GeoRestrictionService.get_client_ip(request)
        country = GeoRestrictionService.get_country_from_ip(client_ip)
        
        if not country:
            logger.warning(f"Could not determine country for IP {client_ip} accessing {feature_name}")
            return True  # Allow if we can't determine
        
        return country in allowed_countries


def require_geo_access(feature_name: str = "load_board", allowed_countries: Optional[List[str]] = None):
    """
    Decorator to enforce geographic access policies on endpoints.
    
    Usage:
        @router.get("/load-board")
        @require_geo_access(feature_name="load_board", allowed_countries=["US", "CA"])
        async def get_load_board(request: Request):
            ...
    """
    if allowed_countries is None:
        allowed_countries = GeoRestrictionService.LOAD_BOARD_ALLOWED_COUNTRIES
    
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get client IP
            client_ip = GeoRestrictionService.get_client_ip(request)
            
            # Check geo restriction
            is_allowed = GeoRestrictionService.check_geo_restriction(
                request, feature_name, allowed_countries
            )
            
            if not is_allowed:
                country = GeoRestrictionService.get_country_from_ip(client_ip)
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": f"{feature_name} access restricted",
                        "message": f"This feature is only available in {', '.join(allowed_countries)}",
                        "allowed_countries": allowed_countries,
                        "detected_country": country,
                        "client_ip": client_ip
                    }
                )
            
            # Allowed - proceed
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


async def validate_load_board_access(request: Request) -> bool:
    """
    Convenience validator for Load Board geo-access checks.
    Useful in endpoints that do not use the decorator.
    
    Usage:
        if not await validate_load_board_access(request):
            raise HTTPException(...)
    """
    client_ip = GeoRestrictionService.get_client_ip(request)
    return GeoRestrictionService.is_ip_allowed_for_load_board(client_ip)


# Log all geo-restricted access attempts
class GeoAccessLogger:
    """Structured logger for geo-restricted feature access attempts."""
    
    @staticmethod
    def log_access_attempt(
        ip_address: str,
        country: Optional[str],
        feature: str,
        allowed: bool,
        user_email: Optional[str] = None
    ):
        """Log geo-access attempt metadata and decision outcome."""
        status_emoji = "✅" if allowed else "❌"
        country_display = country or "Unknown"
        
        log_message = (
            f"{status_emoji} Geo Access: "
            f"IP={ip_address} | "
            f"Country={country_display} | "
            f"Feature={feature} | "
            f"Allowed={allowed}"
        )
        
        if user_email:
            log_message += f" | User={user_email}"
        
        logger.info(log_message)
        
        if allowed:
            logger.info(log_message)
        else:
            logger.warning(log_message)
