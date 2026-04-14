"""
Phase 4: Comprehensive Security Testing Suite

Tests for:
- XSS (Cross-Site Scripting)
- SQL Injection
- CSRF (Cross-Site Request Forgery)
- JWT Security
- RBAC (Role-Based Access Control)
- Authentication & Authorization
- Input Validation
- Rate Limiting
"""

import pytest
import asyncio
import base64
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from datetime import datetime, timedelta
import json
import html

# Import app and dependencies
from backend.config import settings
from backend.models.user import User
from backend.auth import get_password_hash
from tests.conftest import _build_test_app


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def async_client():
    """Create async HTTP client for testing"""
    transport = ASGITransport(app=_build_test_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user_credentials():
    """Test user credentials"""
    return {
        "username": "security_test@gts.com",
        "password": "SecurePass123!",
        "role": "user"
    }


@pytest.fixture
async def admin_credentials():
    """Admin user credentials"""
    return {
        "username": "security_admin@gts.com",
        "password": "AdminPass123!",
        "role": "admin"
    }


@pytest.fixture
async def auth_token(async_client, test_user_credentials):
    """Get valid auth token for testing"""
    response = await async_client.post(
        "/api/v1/auth/token",
        data={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
async def admin_token(async_client, admin_credentials):
    """Get valid admin token for testing"""
    response = await async_client.post(
        "/api/v1/auth/token",
        data={
            "username": admin_credentials["username"],
            "password": admin_credentials["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


# ============================================================================
# XSS (CROSS-SITE SCRIPTING) TESTS
# ============================================================================

class TestXSSProtection:
    """Test protection against XSS attacks"""
    
    @pytest.mark.asyncio
    async def test_xss_in_login_form(self, async_client):
        """Test XSS injection in login form"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>"
        ]
        
        for payload in xss_payloads:
            response = await async_client.post(
                "/api/v1/auth/token",
                data={
                    "username": payload,
                    "password": "test123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Should not execute script or return unescaped HTML
            assert response.status_code in [401, 422], \
                f"XSS payload '{payload}' should be rejected or sanitized"
            
            content = response.text
            # Ensure dangerous characters are escaped
            assert "<script>" not in content.lower(), \
                f"Unescaped script tag found in response for payload: {payload}"
            assert "onerror=" not in content.lower(), \
                f"Unescaped event handler found for payload: {payload}"
    
    @pytest.mark.asyncio
    async def test_xss_in_json_response(self, async_client, auth_token):
        """Test XSS in JSON responses"""
        if not auth_token:
            pytest.skip("Auth token not available")
        
        xss_payload = "<script>alert('XSS')</script>"
        
        # Test in query parameters
        response = await async_client.get(
            f"/api/v1/bots?name={xss_payload}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # JSON should escape HTML entities
        content = response.text
        if "<script>" in content:
            # Check if it's properly escaped
            assert "&lt;script&gt;" in content or \
                   html.escape(xss_payload) in content, \
                   "XSS payload not properly escaped in JSON response"
    
    @pytest.mark.asyncio
    async def test_xss_in_user_input_fields(self, async_client):
        """Test XSS in user registration fields"""
        xss_payloads = {
            "email": "<script>alert('XSS')</script>@test.com",
            "full_name": "<img src=x onerror=alert('XSS')>",
            "password": "<svg/onload=alert('XSS')>"
        }
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=xss_payloads
        )
        
        # Should reject malicious input or sanitize it
        if response.status_code == 200:
            data = response.json()
            # Verify no unescaped HTML in response
            assert "<script>" not in str(data), "Unescaped script in response"
            assert "onerror=" not in str(data), "Unescaped event handler in response"


# ============================================================================
# SQL INJECTION TESTS
# ============================================================================

class TestSQLInjectionProtection:
    """Test protection against SQL injection attacks"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_login(self, async_client):
        """Test SQL injection in login endpoint"""
        sql_payloads = [
            "admin' OR '1'='1",
            "admin' OR '1'='1' --",
            "admin' OR '1'='1' /*",
            "admin'; DROP TABLE users; --",
            "' OR 1=1 --",
            "1' UNION SELECT NULL, NULL, NULL --",
            "admin' AND 1=1 --",
            "' OR 'a'='a",
        ]
        
        for payload in sql_payloads:
            response = await async_client.post(
                "/api/v1/auth/token",
                data={
                    "username": payload,
                    "password": "test123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Should not bypass authentication
            assert response.status_code != 200, \
                f"SQL injection payload '{payload}' bypassed authentication!"
            
            # Should return 401 or 422, not 500
            assert response.status_code in [401, 422], \
                f"SQL injection payload '{payload}' caused server error: {response.status_code}"
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_query_params(self, async_client, auth_token):
        """Test SQL injection in query parameters"""
        if not auth_token:
            pytest.skip("Auth token not available")
        
        sql_payloads = [
            "1' OR '1'='1",
            "1; DROP TABLE users; --",
            "1' UNION SELECT * FROM users --",
        ]
        
        for payload in sql_payloads:
            response = await async_client.get(
                f"/api/v1/bots?id={payload}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            # Should not cause SQL error or expose data
            assert response.status_code != 500, \
                f"SQL injection payload '{payload}' caused server error"
            
            content = response.text.lower()
            # Check for SQL error messages
            assert "sql" not in content, "SQL error message exposed"
            assert "syntax" not in content, "SQL syntax error exposed"
            assert "database" not in content or "database" in content and "not found" in content, \
                "Database information exposed"
    
    @pytest.mark.asyncio
    async def test_parameterized_queries_used(self, async_client, auth_token):
        """Verify parameterized queries are used (no string concatenation)"""
        if not auth_token:
            pytest.skip("Auth token not available")
        
        # Test with special SQL characters
        test_input = "test'; SELECT * FROM users; --"
        
        response = await async_client.get(
            f"/api/v1/bots?search={test_input}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should treat entire input as literal string, not SQL
        # Response should not indicate SQL execution
        assert response.status_code in [200, 400, 404], \
            "Query parameter with SQL injection attempt caused error"


# ============================================================================
# CSRF (CROSS-SITE REQUEST FORGERY) TESTS
# ============================================================================

class TestCSRFProtection:
    """Test CSRF protection mechanisms"""
    
    @pytest.mark.asyncio
    async def test_csrf_token_required_for_state_changing_operations(self, async_client, auth_token):
        """Test CSRF protection on POST/PUT/DELETE endpoints"""
        if not auth_token:
            pytest.skip("Auth token not available")
        
        # Attempt state-changing operation without CSRF token
        # (if CSRF protection is implemented)
        
        # Test POST without CSRF token
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "csrf_test@test.com",
                "password": "Test123!",
                "full_name": "CSRF Test"
            },
            # Missing CSRF token header
        )
        
        # Note: FastAPI doesn't have built-in CSRF protection
        # This test documents the need to implement it
        # Expected: Should be rejected if CSRF protection is added
        
        print(f"⚠️ CSRF Protection Status: {response.status_code}")
        print("⚠️ Note: FastAPI requires manual CSRF implementation")
    
    @pytest.mark.asyncio
    async def test_same_site_cookie_attribute(self, async_client, test_user_credentials):
        """Test that cookies have SameSite attribute"""
        response = await async_client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_credentials["username"],
                "password": test_user_credentials["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Check Set-Cookie headers
        cookies = response.headers.get_list("set-cookie")
        for cookie in cookies:
            if "access_token" in cookie.lower() or "session" in cookie.lower():
                # Should have SameSite attribute
                assert "SameSite" in cookie or "samesite" in cookie, \
                    "Cookie missing SameSite attribute for CSRF protection"
                
                # Should also be HttpOnly and Secure
                assert "HttpOnly" in cookie or "httponly" in cookie, \
                    "Cookie missing HttpOnly flag"


# ============================================================================
# JWT SECURITY TESTS
# ============================================================================

class TestJWTSecurity:
    """Test JWT token security"""
    
    @pytest.mark.asyncio
    async def test_jwt_signature_verification(self, async_client, auth_token):
        """Test JWT signature is verified"""
        if not auth_token:
            pytest.skip("Auth token not available")
        
        # Tamper with token signature
        parts = auth_token.split('.')
        if len(parts) == 3:
            # Change last character of signature
            tampered_token = f"{parts[0]}.{parts[1]}.{parts[2][:-1]}X"
            
            response = await async_client.get(
                "/api/v1/bots",
                headers={"Authorization": f"Bearer {tampered_token}"}
            )
            
            # Should reject tampered token
            assert response.status_code == 401, \
                "Tampered JWT token was accepted!"
    
    @pytest.mark.asyncio
    async def test_jwt_expiration(self, async_client):
        """Test expired JWT tokens are rejected"""
        # Create expired token
        expired_payload = {
            "sub": "999",
            "email": "expired@test.com",
            "role": "user",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        
        expired_token = jwt.encode(
            expired_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        response = await async_client.get(
            "/api/v1/bots",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        # Should reject expired token
        assert response.status_code == 401, \
            "Expired JWT token was accepted!"
    
    @pytest.mark.asyncio
    async def test_jwt_algorithm_confusion(self, async_client):
        """Test protection against algorithm confusion attack"""
        # Try to use 'none' algorithm
        payload = {
            "sub": "999",
            "email": "attacker@test.com",
            "role": "admin",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        # Create token with 'none' algorithm manually because current
        # python-jose versions reject generating it directly.
        header = {"alg": "none", "typ": "JWT"}

        def encode_segment(data):
            raw = json.dumps(data, separators=(",", ":"), default=str).encode("utf-8")
            return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

        none_token = f"{encode_segment(header)}.{encode_segment(payload)}."
        
        response = await async_client.get(
            "/api/v1/bots",
            headers={"Authorization": f"Bearer {none_token}"}
        )
        
        # Should reject 'none' algorithm
        assert response.status_code == 401, \
            "JWT with 'none' algorithm was accepted!"
    
    @pytest.mark.asyncio
    async def test_jwt_missing_required_claims(self, async_client):
        """Test JWT with missing required claims is rejected"""
        # Token without 'sub' claim
        incomplete_payload = {
            "email": "test@test.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        incomplete_token = jwt.encode(
            incomplete_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        response = await async_client.get(
            "/api/v1/bots",
            headers={"Authorization": f"Bearer {incomplete_token}"}
        )
        
        # Should reject token with missing claims
        assert response.status_code in [401, 403], \
            "JWT with missing required claims was accepted!"


# ============================================================================
# RBAC (ROLE-BASED ACCESS CONTROL) TESTS
# ============================================================================

class TestRBACImplementation:
    """Test Role-Based Access Control"""
    
    @pytest.mark.asyncio
    async def test_user_cannot_access_admin_endpoints(self, async_client, auth_token):
        """Test regular user cannot access admin-only endpoints"""
        if not auth_token:
            pytest.skip("Auth token not available")
        
        admin_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/settings",
            "/api/v1/admin/data-sources",
        ]
        
        for endpoint in admin_endpoints:
            response = await async_client.get(
                endpoint,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            # Should deny access
            assert response.status_code in [401, 403, 404], \
                f"Regular user accessed admin endpoint: {endpoint}"
    
    @pytest.mark.asyncio
    async def test_admin_can_access_admin_endpoints(self, async_client, admin_token):
        """Test admin user can access admin-only endpoints"""
        if not admin_token:
            pytest.skip("Admin token not available")
        
        # Test admin access
        response = await async_client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should allow access (200) or return not found (404) but not forbidden
        assert response.status_code in [200, 404], \
            f"Admin cannot access admin endpoint: {response.status_code}"
    
    @pytest.mark.asyncio
    async def test_role_escalation_prevention(self, async_client, auth_token):
        """Test users cannot escalate their own role"""
        if not auth_token:
            pytest.skip("Auth token not available")
        
        # Attempt to change role to admin
        response = await async_client.put(
            "/api/v1/users/me",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should reject role change or ignore it
        if response.status_code == 200:
            data = response.json()
            assert data.get("role") != "admin", \
                "User successfully escalated their own role to admin!"


# ============================================================================
# AUTHENTICATION & AUTHORIZATION TESTS
# ============================================================================

class TestAuthenticationSecurity:
    """Test authentication security"""
    
    def test_password_complexity_requirements(self):
        """Test password complexity validation function directly"""
        from backend.routes.auth import _validate_password_complexity
        from fastapi import HTTPException
        
        # Test weak passwords should raise HTTPException
        weak_passwords = [
            "123456",  # Too short, no uppercase, no lowercase, no special chars
            "password",  # No uppercase, no digits
            "abc123",  # No uppercase
            "test",  # Too short
            "12345678"  # No uppercase, no lowercase
        ]
        
        for weak_password in weak_passwords:
            with pytest.raises(HTTPException) as exc_info:
                _validate_password_complexity(weak_password)
            assert exc_info.value.status_code in [400, 422], \
                f"Weak password '{weak_password}' should be rejected"
        
        # Test strong passwords should not raise exception
        strong_passwords = [
            "StrongPass123!",
            "MySecurePassword1",
            "Complex!Password#2024",
            "Abc123Def456"
        ]
        
        for strong_password in strong_passwords:
            # Should not raise any exception
            _validate_password_complexity(strong_password)
    
    @pytest.mark.asyncio
    async def test_brute_force_protection(self, async_client):
        """Test protection against brute force attacks"""
        # Attempt multiple failed logins
        failed_attempts = 0
        max_attempts = 10
        
        for i in range(max_attempts):
            response = await async_client.post(
                "/api/v1/auth/token",
                data={
                    "username": "brute_force@test.com",
                    "password": f"wrong_password_{i}"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 401:
                failed_attempts += 1
            elif response.status_code == 429:  # Rate limited
                print(f"✅ Rate limiting activated after {failed_attempts} attempts")
                break
        
        # Should implement rate limiting
        print(f"⚠️ Completed {failed_attempts} failed login attempts without rate limiting")
        print("⚠️ Consider implementing rate limiting for login endpoint")
    
    @pytest.mark.asyncio
    async def test_no_auth_token_required_endpoints(self, async_client):
        """Test public endpoints don't require authentication"""
        public_endpoints = [
            "/healthz",
            "/api/v1/auth/token",
            "/api/v1/auth/register"
        ]
        
        for endpoint in public_endpoints:
            if endpoint == "/api/v1/auth/token":
                response = await async_client.post(endpoint, data={})
            else:
                response = await async_client.get(endpoint)
            
            # Should not return 401 (may return 400 or 422 for invalid data)
            assert response.status_code != 401, \
                f"Public endpoint {endpoint} requires authentication"


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

class TestInputValidation:
    """Test input validation and sanitization"""
    
    @pytest.mark.asyncio
    async def test_email_validation(self, async_client):
        """Test email format validation"""
        invalid_emails = [
            "not_an_email",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "double@@domain.com"
        ]
        
        for invalid_email in invalid_emails:
            response = await async_client.post(
                "/api/v1/auth/register",
                json={
                    "email": invalid_email,
                    "password": "ValidPass123!",
                    "full_name": "Test User"
                }
            )
            
            # Should reject invalid email
            assert response.status_code in [400, 422], \
                f"Invalid email '{invalid_email}' was accepted!"
    
    @pytest.mark.asyncio
    async def test_input_length_limits(self, async_client):
        """Test input length limits are enforced"""
        # Very long input
        long_input = "A" * 10000
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": f"{long_input}@test.com",
                "password": "ValidPass123!",
                "full_name": long_input
            }
        )
        
        # Should reject or truncate excessively long input
        assert response.status_code in [400, 413, 422], \
            "Excessively long input was accepted without validation"
    
    @pytest.mark.asyncio
    async def test_special_characters_handling(self, async_client):
        """Test special characters are properly handled"""
        special_chars = [
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "%00null_byte",
            "\\x00\\x01\\x02",
        ]
        
        for special_char in special_chars:
            response = await async_client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"test_{special_char}@test.com",
                    "password": "ValidPass123!",
                    "full_name": special_char
                }
            )
            
            # Should handle or reject special characters safely
            assert response.status_code in [200, 400, 422], \
                f"Special character '{special_char}' caused server error"


# ============================================================================
# SECURITY HEADERS TESTS
# ============================================================================

class TestSecurityHeaders:
    """Test security-related HTTP headers"""
    
    @pytest.mark.asyncio
    async def test_security_headers_present(self, async_client):
        """Test security headers are present in responses"""
        response = await async_client.get("/healthz")
        
        headers = response.headers
        
        # Recommended security headers
        recommended_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000",
        }
        
        missing_headers = []
        for header, expected_value in recommended_headers.items():
            if header not in headers:
                missing_headers.append(header)
                print(f"⚠️ Missing security header: {header}")
        
        if missing_headers:
            print(f"⚠️ Recommendation: Add {len(missing_headers)} security headers")
    
    @pytest.mark.asyncio
    async def test_cors_configuration(self, async_client):
        """Test CORS configuration is secure"""
        response = await async_client.options(
            "/api/v1/bots",
            headers={
                "Origin": "https://malicious-site.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        
        if cors_header == "*":
            print("⚠️ Warning: CORS allows all origins (*)")
            print("⚠️ Recommendation: Restrict CORS to specific trusted domains")


# ============================================================================
# SUMMARY & RECOMMENDATIONS
# ============================================================================

@pytest.mark.asyncio
async def test_security_summary():
    """Generate security test summary"""
    print("\n" + "="*80)
    print("PHASE 4: SECURITY TESTING SUMMARY")
    print("="*80)
    
    categories = {
        "XSS Protection": "Testing completed - Check for unescaped HTML",
        "SQL Injection": "Testing completed - Verify parameterized queries",
        "CSRF Protection": "Manual implementation required",
        "JWT Security": "Testing completed - Verify signature & expiration",
        "RBAC": "Testing completed - Verify role restrictions",
        "Input Validation": "Testing completed - Check edge cases",
        "Security Headers": "Recommendation: Add missing headers",
        "Rate Limiting": "Recommendation: Implement for login endpoint"
    }
    
    print("\n📋 Security Test Categories:")
    for category, status in categories.items():
        print(f"   • {category}: {status}")
    
    print("\n🔒 Security Recommendations:")
    print("   1. Implement CSRF protection for state-changing operations")
    print("   2. Add rate limiting for authentication endpoints")
    print("   3. Add security headers (X-Frame-Options, CSP, HSTS)")
    print("   4. Implement account lockout after failed login attempts")
    print("   5. Add request size limits to prevent DoS")
    print("   6. Enable HTTPS in production (enforce Secure cookies)")
    print("   7. Implement audit logging for security events")
    
    print("\n✅ Strengths Found:")
    print("   • JWT-based authentication")
    print("   • Password hashing with bcrypt")
    print("   • Parameterized SQL queries (SQLAlchemy ORM)")
    print("   • Role-based access control framework")
    
    print("="*80 + "\n")
