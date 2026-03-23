from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.db.deps import get_db
from backend.models.user import User
from backend.auth import get_password_hash, verify_password
from backend.schemas.user import UserResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import jwt
from backend.config import settings
import logging
import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from backend.utils.auth_cache import cache_user_data, get_cache_stats
from backend.services.platform_settings_store import get_platform_settings
from backend.security.two_factor_auth import TwoFactorAuth, TwoFactorSetup
from backend.utils.crypto import decrypt_secret, encrypt_secret
from backend.utils.email_utils import send_email, send_admin_notification
from backend.security.auth import JWT_SECRET_KEY, JWT_ALGORITHM, _issue_refresh_token, create_access_token
import json

# Phase 3 Optimization: Thread pool for CPU-bound operations (bcrypt)
_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="bcrypt-")

log = logging.getLogger("gts.auth")

router = APIRouter()
REGISTRATION_DISABLED = getattr(settings, "REGISTRATION_DISABLED", True)
_REGISTRATION_DISABLED_DETAIL_BASE = getattr(
    settings,
    "REGISTRATION_DISABLED_DETAIL",
    "Registration is temporarily closed. Please contact the administrator.",
)
REGISTRATION_REOPEN_DATE = getattr(settings, "REGISTRATION_REOPEN_DATE", None)
REGISTRATION_CONTACT_EMAIL = getattr(settings, "REGISTRATION_CONTACT_EMAIL", None)

def _build_registration_detail() -> str:
    parts = [_REGISTRATION_DISABLED_DETAIL_BASE.strip()]
    if REGISTRATION_REOPEN_DATE:
        parts.append(f"Expected to reopen on {REGISTRATION_REOPEN_DATE}.")
    if REGISTRATION_CONTACT_EMAIL:
        parts.append(f"Contact: {REGISTRATION_CONTACT_EMAIL}.")
    return " ".join([p for p in parts if p]).strip()

REGISTRATION_DISABLED_DETAIL = _build_registration_detail()


async def _get_security_settings(db: AsyncSession) -> dict:
	defaults = {
		"minPasswordLength": 8,
		"requireUppercase": True,
		"requireLowercase": True,
		"requireNumbers": True,
		"requireSpecialChars": True,
		"passwordExpiryDays": 90,
		"maxFailedAttempts": 5,
		"lockoutDuration": 30,
		"allowMultiSession": True,
		"enable2FA": False,
	}
	try:
		settings = await get_platform_settings(db)
		security = settings.get("security", {}) or {}
		merged = {**defaults, **security}
		return merged
	except Exception:
		return defaults


def _encrypt_tfa_secret(secret: str) -> str:
	try:
		encrypted = encrypt_secret(secret)
		return encrypted or secret
	except Exception:
		return secret


def _decrypt_tfa_secret(secret: Optional[str]) -> Optional[str]:
	if not secret:
		return None
	try:
		decrypted = decrypt_secret(secret)
		return decrypted or secret
	except Exception:
		return secret


def _load_backup_codes(raw: Optional[str]) -> list[str]:
	if not raw:
		return []
	try:
		codes = json.loads(raw)
		return [str(code) for code in codes if code]
	except Exception:
		return []


def _save_backup_codes(codes: list[str]) -> str:
	return json.dumps(codes)


async def _record_failed_login(user: User, security: dict, db: AsyncSession) -> None:
	# Safely handle case where columns don't exist yet
	try:
		failed_attempts = int(getattr(user, "failed_login_attempts", 0) or 0) + 1
		user.failed_login_attempts = failed_attempts
		max_failed = int(security.get("maxFailedAttempts", 5) or 5)
		lockout_minutes = int(security.get("lockoutDuration", 0) or 0)

		if lockout_minutes > 0 and failed_attempts >= max_failed:
			user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=lockout_minutes)

		db.add(user)
		await db.commit()
	except Exception as e:
		log.warning(f"Failed to record login attempt: {e}")
		# Don't fail the login process due to absence of security columns


async def _reset_failed_login(user: User, db: AsyncSession) -> None:
	try:
		user.failed_login_attempts = 0
		user.lockout_until = None
		db.add(user)
		await db.commit()
	except Exception as e:
		log.warning(f"Failed to reset login attempts: {e}")
		# Don't fail the login process


def _send_login_notification_to_user(user_email: str, ip_address: str, user_agent: str) -> None:
	subject = "New login to your GTS account"
	body = f"""<!DOCTYPE html>
<html>
	<body style=\"margin:0;padding:24px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;\">
		<h2 style=\"margin:0 0 12px;color:#ffffff;\">New login detected</h2>
		<p style=\"margin:0 0 8px;\">Your account was accessed successfully.</p>
		<p style=\"margin:0 0 6px;color:#cbd5e1;\"><strong>Account:</strong> {user_email}</p>
		<p style=\"margin:0 0 6px;color:#cbd5e1;\"><strong>IP:</strong> {ip_address}</p>
		<p style=\"margin:0 0 12px;color:#cbd5e1;\"><strong>Device:</strong> {user_agent}</p>
		<p style=\"margin:0;color:#cbd5e1;\">If this was not you, reset your password immediately.</p>
	</body>
</html>"""
	send_email(subject=subject, body=body, to=[user_email], html=True)


def _send_login_notification_to_admin(user_email: str, ip_address: str, user_agent: str) -> None:
	subject = "User login alert"
	body = f"""<!DOCTYPE html>
<html>
	<body style=\"margin:0;padding:20px;font-family:Arial,sans-serif;background-color:#0b1220;color:#e2e8f0;\">
		<h3 style=\"margin:0 0 10px;color:#ffffff;\">Successful user login</h3>
		<p style=\"margin:0 0 6px;color:#cbd5e1;\"><strong>User:</strong> {user_email}</p>
		<p style=\"margin:0 0 6px;color:#cbd5e1;\"><strong>IP:</strong> {ip_address}</p>
		<p style=\"margin:0;color:#cbd5e1;\"><strong>Device:</strong> {user_agent}</p>
	</body>
</html>"""
	send_admin_notification(subject=subject, body=body, html=True)

async def validate_password_strength(password: str, db: AsyncSession) -> None:
	"""
	Validate password complexity requirements using platform security settings.

	Raises:
		HTTPException: 400 if password doesn't meet requirements
	"""
	security = await _get_security_settings(db)
	errors = []

	min_length = int(security.get("minPasswordLength", 8) or 8)
	require_uppercase = bool(security.get("requireUppercase", True))
	require_lowercase = bool(security.get("requireLowercase", True))
	require_numbers = bool(security.get("requireNumbers", True))
	require_special = bool(security.get("requireSpecialChars", True))

	if len(password) < min_length:
		errors.append(f"Password must be at least {min_length} characters long")

	if require_uppercase and not re.search(r"[A-Z]", password):
		errors.append("Password must contain at least one uppercase letter")

	if require_lowercase and not re.search(r"[a-z]", password):
		errors.append("Password must contain at least one lowercase letter")

	if require_numbers and not re.search(r"[0-9]", password):
		errors.append("Password must contain at least one number")

	if require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/;'`~]", password):
		errors.append("Password must contain at least one special character")

	if errors:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=" | ".join(errors)
		)

# Registration payload
class RegisterRequest(BaseModel):
	email: EmailStr
	password: str
	full_name: Optional[str] = None


class TwoFactorSetupInitRequest(BaseModel):
	email: EmailStr
	password: str


class TwoFactorVerifyLoginRequest(BaseModel):
	email: EmailStr
	password: str
	token: str
	backup_code: Optional[str] = None

@router.post("/auth/register", response_model=UserResponse)
async def register_user(
	request: RegisterRequest,
	db: AsyncSession = Depends(get_db)
):
	"""Register a new user"""
	if REGISTRATION_DISABLED:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=REGISTRATION_DISABLED_DETAIL,
		)
	try:
		# 1. Check if user already exists
		result = await db.execute(
			select(User).where(User.email == request.email)
		)
		existing_user = result.scalar_one_or_none()
		if existing_user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Email already registered"
			)
		
		# 2. Validate password strength using platform security settings
		await validate_password_strength(request.password, db)
		
		# 3. Hash password (Phase 3: Run bcrypt in thread pool)
		loop = asyncio.get_event_loop()
		hashed_password = await loop.run_in_executor(
			_executor,
			get_password_hash,
			request.password
		)
		
		# 4. Create new user
		now = datetime.now(timezone.utc)
		new_user = User(
			email=request.email,
			hashed_password=hashed_password,
			full_name=request.full_name or request.email.split('@')[0],
			role="user",  # default role
			is_active=True,
			password_changed_at=now,
			failed_login_attempts=0,
			two_factor_enabled=False,
		)
		# 5. Persist to database
		db.add(new_user)
		await db.commit()
		await db.refresh(new_user)
		# 6. Log success
		log.info("New user registered: %s", new_user.email)
		# 7. Return data without password
		return {
			"id": new_user.id,
			"email": new_user.email,
			"full_name": new_user.full_name,
			"role": new_user.role,
			"is_active": new_user.is_active,
			"created_at": new_user.created_at
		}
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()  # Phase 4 Fix: await rollback
		log.error("Registration error: %s", str(e))
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Server error: {str(e)}"
		)

@router.post("/auth/token")
async def login_for_access_token(
	request: Request,
	form_data: OAuth2PasswordRequestForm = Depends(),
	db: AsyncSession = Depends(get_db)
):
	"""Sign in and get access token"""
	try:
		log.info("Login attempt: %s", form_data.username)
		security = await _get_security_settings(db)
		now = datetime.now(timezone.utc)
		# 1. Find user
		result = await db.execute(
			select(User).where(User.email == form_data.username)
		)
		user = result.scalar_one_or_none()
		if not user:
			log.warning("User not found: %s", form_data.username)
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid credentials",
				headers={"WWW-Authenticate": "Bearer"},
			)

		# 1.1 Lockout check - gracefully handle missing columns
		try:
			if user.lockout_until and user.lockout_until > now:
				raise HTTPException(
					status_code=status.HTTP_403_FORBIDDEN,
					detail=f"Account locked until {user.lockout_until.isoformat()}"
				)
		except AttributeError:
			pass  # Columns don't exist yet, skip check
		# 2. Verify password (Phase 3: Run bcrypt in thread pool)
		stored_hash = getattr(user, "password_hash", None) or getattr(user, "hashed_password", None)
		if not stored_hash:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Server misconfig: user password hash field missing"
			)
		# Run bcrypt verification in thread pool to avoid blocking event loop
		loop = asyncio.get_event_loop()
		is_valid = await loop.run_in_executor(
			_executor,
			verify_password,
			form_data.password,
			stored_hash
		)
		if not is_valid:
			log.warning("Wrong password for user: %s", form_data.username)
			await _record_failed_login(user, security, db)
			# Check lockout status again after recording attempt
			try:
				if user.lockout_until and user.lockout_until > now:
					raise HTTPException(
						status_code=status.HTTP_403_FORBIDDEN,
						detail=f"Account locked until {user.lockout_until.isoformat()}"
					)
			except AttributeError:
				pass  # Columns don't exist yet, skip check
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid credentials",
				headers={"WWW-Authenticate": "Bearer"},
			)
		# 3. Ensure account is active
		if not user.is_active:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Account is not active"
			)

		# 3.1 Password expiry check - only if password_changed_at is explicitly set
		# (for legacy users, we allow them to login without expiry)
		expiry_days = int(security.get("passwordExpiryDays", 0) or 0)
		if expiry_days > 0 and user.password_changed_at:
			# Only check expiry for users who have explicitly changed their password
			if (now - user.password_changed_at) > timedelta(days=expiry_days):
				raise HTTPException(
					status_code=status.HTTP_403_FORBIDDEN,
					detail="Password expired. Please reset your password."
				)

		# 3.2 Enforce 2FA if enabled at platform level
		# TEMPORARILY DISABLED FOR DEVELOPMENT
		# if bool(security.get("enable2FA", False)):
		# 	if not user.two_factor_enabled or not user.two_factor_secret:
		# 		raise HTTPException(
		# 			status_code=status.HTTP_403_FORBIDDEN,
		# 			detail={"error": "Two-factor authentication setup required", "setup_required": True}
		# 		)
		#
		# 	try:
		# 		form = await request.form()
		# 		token = str(form.get("otp") or "").strip()
		# 		backup_code = str(form.get("backup_code") or "").strip()
		# 	except Exception:
		# 		token = ""
		# 		backup_code = ""
		#
		# 	secret = _decrypt_tfa_secret(user.two_factor_secret)
		# 	is_valid_token = bool(secret) and bool(token) and TwoFactorAuth.verify_token(secret, token)
		# 	used_backup = False
		# 	if not is_valid_token and backup_code:
		# 		codes = _load_backup_codes(user.two_factor_backup_codes)
		# 		if backup_code in codes:
		# 			codes = [c for c in codes if c != backup_code]
		# 			user.two_factor_backup_codes = _save_backup_codes(codes)
		# 			used_backup = True
		#
		# 	if not is_valid_token and not used_backup:
		# 		await _record_failed_login(user, security, db)
		# 		raise HTTPException(
		# 			status_code=status.HTTP_401_UNAUTHORIZED,
		# 			detail={"error": "Invalid two-factor code", "two_factor_required": True}
		# 		)

		# Reset failed attempts on success
		await _reset_failed_login(user, db)

		# 3.5 Update last login timestamp and session version
		user.last_login = now
		# Safely update password_changed_at if columns exist
		try:
			if not user.password_changed_at:
				user.password_changed_at = now
		except AttributeError:
			pass  # Column doesn't exist yet
		# Update token version for multi-session control
		try:
			if not bool(security.get("allowMultiSession", True)):
				user.token_version = int(getattr(user, "token_version", 0) or 0) + 1
		except Exception:
			pass  # Column or setting doesn't exist
		db.add(user)
		await db.commit()
		await db.refresh(user)
		# 4. Create token
		access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
		access_token = jwt.encode(
			{
				"sub": str(user.id),
				"email": user.email,
				"role": user.role,
				"iat": datetime.utcnow(),
				"exp": datetime.utcnow() + access_token_expires,
				"tv": int(getattr(user, "token_version", 0) or 0),
			},
			JWT_SECRET_KEY,
			algorithm=JWT_ALGORITHM
		)
		log.info("Token created for user: %s", user.email)
		try:
			refresh_token = await _issue_refresh_token(db, int(user.id))
		except Exception as refresh_error:
			log.error("Failed to issue refresh token for %s: %s", user.email, refresh_error)
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Failed to issue refresh token"
			)
		
		# Phase 3: Cache user data to reduce DB load on subsequent requests
		cache_user_data(access_token, {
			"id": user.id,
			"email": user.email,
			"role": user.role,
			"is_active": user.is_active
		})
		
		# 5. Return token
		client_ip = getattr(request.client, "host", None) or "unknown"
		user_agent = request.headers.get("user-agent", "unknown")
		try:
			asyncio.create_task(asyncio.to_thread(_send_login_notification_to_user, user.email, client_ip, user_agent))
			asyncio.create_task(asyncio.to_thread(_send_login_notification_to_admin, user.email, client_ip, user_agent))
		except Exception as notify_error:
			log.warning("Login email notification skipped for %s: %s", user.email, notify_error)

		return {
			"access_token": access_token,
			"refresh_token": refresh_token,
			"token_type": "bearer",
			"expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
			"user": {
				"id": user.id,
				"email": user.email,
				"full_name": getattr(user, "full_name", None),
				"role": user.role,
			},
		}
	except HTTPException:
		raise
	except Exception as e:
		log.error("Login error: %s", str(e))
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Server error: {str(e)}"
		)


@router.post("/auth/2fa/setup-init", response_model=TwoFactorSetup)
async def setup_2fa_init(
	payload: TwoFactorSetupInitRequest,
	db: AsyncSession = Depends(get_db)
):
	"""Initialize 2FA setup with email/password, returns QR code and backup codes."""
	security = await _get_security_settings(db)
	result = await db.execute(select(User).where(User.email == payload.email))
	user = result.scalar_one_or_none()
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	now = datetime.now(timezone.utc)
	if user.lockout_until and user.lockout_until > now:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=f"Account locked until {user.lockout_until.isoformat()}"
		)

	stored_hash = getattr(user, "password_hash", None) or getattr(user, "hashed_password", None)
	if not stored_hash:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server misconfig: user password hash field missing"
		)

	loop = asyncio.get_event_loop()
	is_valid = await loop.run_in_executor(
		_executor,
		verify_password,
		payload.password,
		stored_hash
	)
	if not is_valid:
		await _record_failed_login(user, security, db)
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	tfa = TwoFactorAuth()
	secret = tfa.generate_secret()
	qr_code = tfa.generate_qr_code(user.email, secret)
	backup_codes = tfa.generate_backup_codes()

	user.two_factor_secret = _encrypt_tfa_secret(secret)
	user.two_factor_backup_codes = _save_backup_codes(backup_codes)
	user.two_factor_enabled = False
	user.failed_login_attempts = 0
	user.lockout_until = None
	user.updated_at = now
	await db.commit()
	await db.refresh(user)

	return TwoFactorSetup(
		secret=secret,
		qr_code=qr_code,
		backup_codes=backup_codes,
		manual_entry_key=secret,
	)


@router.post("/auth/2fa/verify-login")
async def verify_2fa_login(
	payload: TwoFactorVerifyLoginRequest,
	db: AsyncSession = Depends(get_db)
):
	"""Verify 2FA token and return access token."""
	security = await _get_security_settings(db)
	result = await db.execute(select(User).where(User.email == payload.email))
	user = result.scalar_one_or_none()
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	now = datetime.now(timezone.utc)
	if user.lockout_until and user.lockout_until > now:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=f"Account locked until {user.lockout_until.isoformat()}"
		)

	stored_hash = getattr(user, "password_hash", None) or getattr(user, "hashed_password", None)
	if not stored_hash:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server misconfig: user password hash field missing"
		)

	loop = asyncio.get_event_loop()
	is_valid = await loop.run_in_executor(
		_executor,
		verify_password,
		payload.password,
		stored_hash
	)
	if not is_valid:
		await _record_failed_login(user, security, db)
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	secret = _decrypt_tfa_secret(user.two_factor_secret)
	if not secret:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA is not set up")

	valid_token = TwoFactorAuth.verify_token(secret, payload.token)
	used_backup = False
	if not valid_token and payload.backup_code:
		codes = _load_backup_codes(user.two_factor_backup_codes)
		if payload.backup_code in codes:
			codes = [c for c in codes if c != payload.backup_code]
			user.two_factor_backup_codes = _save_backup_codes(codes)
			used_backup = True

	if not valid_token and not used_backup:
		await _record_failed_login(user, security, db)
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid 2FA code")

	user.two_factor_enabled = True
	user.last_login = now
	if not user.password_changed_at:
		user.password_changed_at = now
	if not bool(security.get("allowMultiSession", True)):
		user.token_version = int(getattr(user, "token_version", 0) or 0) + 1
	user.failed_login_attempts = 0
	user.lockout_until = None
	await db.commit()
	await db.refresh(user)

	access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = jwt.encode(
		{
			"sub": str(user.id),
			"email": user.email,
			"role": user.role,
			"iat": datetime.utcnow(),
			"exp": datetime.utcnow() + access_token_expires,
			"tv": int(getattr(user, "token_version", 0) or 0),
		},
		JWT_SECRET_KEY,
		algorithm=JWT_ALGORITHM
	)

	try:
		refresh_token = await _issue_refresh_token(db, int(user.id))
	except Exception as refresh_error:
		log.error("Failed to issue refresh token after 2FA for %s: %s", user.email, refresh_error)
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to issue refresh token"
		)

	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"token_type": "bearer",
		"expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
		"user": {
			"id": user.id,
			"email": user.email,
			"full_name": getattr(user, "full_name", None),
			"role": user.role,
		},
	}


@router.get("/auth/cache/stats")
async def get_auth_cache_stats():
	"""Get authentication cache statistics (Phase 3 monitoring)"""
	stats = get_cache_stats()
	return {
		"cache_stats": stats,
		"optimization_level": "Phase 3 - Thread Pool + In-Memory Cache"
	}


@router.get("/auth/dev-token")
async def get_dev_token(role: str = "admin", secret: Optional[str] = None):
	"""Development token endpoint for testing (only in dev mode)"""
	if os.getenv("APP_ENV") == "production":
		raise HTTPException(status_code=404, detail="Not found")
	
	# Simple secret check for dev mode
	expected_secret = os.getenv("DEV_SECRET", "dev-secret-123")
	if secret != expected_secret:
		raise HTTPException(status_code=403, detail="Invalid secret")
	
	# Create a dev token
	token = create_access_token(
		subject="dev-user",
		email="dev@gts.local",
		role=role,
		expires_delta=timedelta(hours=24)
	)
	
	return {"access_token": token, "token_type": "bearer", "role": role}
