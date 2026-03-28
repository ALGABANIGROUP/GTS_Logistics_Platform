"""
Unified Authentication System for GTS
Supports centralized login for multiple systems (Main GTS + TMS)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import text
import logging

from backend.models.user import User
from backend.models.unified_models import UserSystemsAccess
from backend.core.settings import settings

logger = logging.getLogger(__name__)

class UnifiedAuthSystem:
    """Unified authentication system with dual permissions"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = settings.JWT_SECRET_KEY or settings.SECRET_KEY or "development-placeholder-not-for-production"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Session timeout: 15 minutes of inactivity
        env = (settings.APP_ENV or "development").strip().lower()
        if env in {"production", "prod"} and self.SECRET_KEY == "development-placeholder-not-for-production":
            raise RuntimeError("Unified auth secret must not use the development default in production.")
    
    def hash_password(self, password: str) -> str:
        """Hash the password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password correctness"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def authenticate_user(self, session, email: str, password: str):
        """
        Authenticate user credentials
        
        Returns:
            dict: User data + available systems
        """
        
        # Search for user
        user_result = await session.execute(
            text("SELECT id, email, full_name, is_active, password_hash FROM users WHERE email = :email"),
            {"email": email},
        )
        user = user_result.mappings().first()
        
        if not user:
            logger.warning(f"Failed login attempt: User {email} not found")
            return None
        
        # Verify password
        if not self.verify_password(password, str(user["password_hash"])):
            logger.warning(f"Failed login attempt: Incorrect password for user {email}")
            return None
        
        # Get available systems
        access_result = await session.execute(
            text(
                """
                SELECT system_type, access_level
                FROM user_systems_access
                WHERE user_id = :user_id AND is_active = TRUE
                """
            ),
            {"user_id": str(user["id"])},
        )
        systems = [
            {"system_type": row["system_type"], "access_level": row["access_level"]}
            for row in access_result.mappings().all()
        ]
        
        return {
            "user_id": str(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "is_active": user["is_active"],
            "systems": systems,
        }
    
    def create_access_token(
        self, 
        user_id: str, 
        email: str, 
        systems: List[Dict],
        current_system: Optional[str] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT token with system information
        
        Args:
            user_id: User identifier
            email: Email address
            systems: List of available systems
            current_system: Currently selected system
            expires_delta: Token expiration duration
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": user_id,
            "email": email,
            "systems": systems,
            "current_system": current_system or (systems[0]["system_type"] if systems else None),
            "iat": datetime.utcnow(),
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.SECRET_KEY, 
            algorithm=self.ALGORITHM
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify token validity and extract data
        """
        try:
            payload = jwt.decode(
                token, 
                self.SECRET_KEY, 
                algorithms=[self.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"Token error: {str(e)}")
            return None
    
    def switch_system(
        self, 
        token: str, 
        new_system: str
    ) -> Optional[str]:
        """
        Switch current system with new token issuance
        """
        payload = self.verify_token(token)
        
        if not payload:
            return None
        
        # Verify system exists in available systems list
        available_systems = [s["system_type"] for s in payload.get("systems", [])]
        
        if new_system not in available_systems:
            logger.warning(f"Attempt to access unauthorized system: {new_system}")
            return None
        
        # Create new token with selected system
        new_token = self.create_access_token(
            user_id=payload["sub"],
            email=payload["email"],
            systems=payload["systems"],
            current_system=new_system
        )
        
        logger.info(f"System switch: {payload['current_system']} -> {new_system}")
        
        return new_token


# Create single instance of the system
unified_auth = UnifiedAuthSystem()

