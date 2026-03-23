"""
Two-Factor Authentication (2FA) implementation for GTS Logistics.
Supports TOTP (Time-based One-Time Password) using authenticator apps.
"""
from __future__ import annotations

import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple
from pydantic import BaseModel


class TwoFactorAuth:
    """Handle 2FA operations using TOTP."""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new 2FA secret key."""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(email: str, secret: str, issuer: str = "GTS Logistics") -> str:
        """
        Generate QR code for authenticator app setup.
        Returns base64-encoded PNG image.
        """
        # Create provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name=issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def verify_token(secret: str, token: str, window: int = 1) -> bool:
        """
        Verify a TOTP token.
        
        Args:
            secret: User's 2FA secret key
            token: 6-digit code from authenticator app
            window: Number of time periods to check (allows for clock drift)
        
        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)
    
    @staticmethod
    def generate_backup_codes(count: int = 8) -> list[str]:
        """
        Generate backup codes for 2FA recovery.
        Returns list of random 8-character codes.
        """
        import secrets
        import string
        
        codes = []
        alphabet = string.ascii_uppercase + string.digits
        for _ in range(count):
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            # Format as XXXX-XXXX for readability
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        
        return codes


class TwoFactorSetup(BaseModel):
    """Response model for 2FA setup."""
    secret: str
    qr_code: str
    backup_codes: list[str]
    manual_entry_key: str


class TwoFactorVerify(BaseModel):
    """Request model for 2FA verification."""
    token: str
    remember_device: bool = False


class BackupCodeVerify(BaseModel):
    """Request model for backup code verification."""
    backup_code: str


# OAuth2 Provider configurations
class OAuth2Provider:
    """OAuth2 provider configuration."""
    
    GOOGLE = {
        "name": "Google",
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
    }
    
    MICROSOFT = {
        "name": "Microsoft",
        "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
        "scope": "openid email profile User.Read",
    }
    
    GITHUB = {
        "name": "GitHub",
        "authorization_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scope": "read:user user:email",
    }


class OAuth2Config(BaseModel):
    """OAuth2 configuration for a provider."""
    provider: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str


def build_authorization_url(
    provider: str,
    client_id: str,
    redirect_uri: str,
    state: str,
    scope: Optional[str] = None
) -> str:
    """
    Build OAuth2 authorization URL.
    
    Args:
        provider: OAuth2 provider name (google, microsoft, github)
        client_id: OAuth2 client ID
        redirect_uri: Callback URL
        state: CSRF protection state token
        scope: Optional custom scope (uses default if not provided)
    
    Returns:
        Full authorization URL
    """
    from urllib.parse import urlencode
    
    provider_config = {
        "google": OAuth2Provider.GOOGLE,
        "microsoft": OAuth2Provider.MICROSOFT,
        "github": OAuth2Provider.GITHUB,
    }.get(provider.lower())
    
    if not provider_config:
        raise ValueError(f"Unsupported OAuth2 provider: {provider}")
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope or provider_config["scope"],
        "state": state,
    }
    
    return f"{provider_config['authorization_url']}?{urlencode(params)}"


# Example usage in routes:
"""
# In auth_routes.py:

@router.post("/auth/2fa/setup")
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Generate 2FA secret
    tfa = TwoFactorAuth()
    secret = tfa.generate_secret()
    qr_code = tfa.generate_qr_code(current_user.email, secret)
    backup_codes = tfa.generate_backup_codes()
    
    # Store secret in database (hashed)
    current_user.tfa_secret = secret
    current_user.tfa_backup_codes = backup_codes  # Store hashed
    await db.commit()
    
    return TwoFactorSetup(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes,
        manual_entry_key=secret
    )


@router.post("/auth/2fa/verify")
async def verify_2fa(
    verification: TwoFactorVerify,
    current_user: User = Depends(get_current_user)
):
    tfa = TwoFactorAuth()
    
    if not current_user.tfa_secret:
        raise HTTPException(400, "2FA not enabled")
    
    if not tfa.verify_token(current_user.tfa_secret, verification.token):
        raise HTTPException(401, "Invalid 2FA code")
    
    # Mark as verified, issue session token
    return {"verified": True, "access_token": "..."}


@router.get("/auth/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in session or cache
    # ...
    
    # Build authorization URL
    auth_url = build_authorization_url(
        provider=provider,
        client_id=os.getenv(f"{provider.upper()}_CLIENT_ID"),
        redirect_uri=f"{request.base_url}auth/oauth/{provider}/callback",
        state=state
    )
    
    return RedirectResponse(auth_url)


@router.get("/auth/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    # Verify state token
    # Exchange code for access token
    # Fetch user info
    # Create or login user
    # Issue JWT
    pass
"""
