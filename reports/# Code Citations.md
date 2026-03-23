# Code Citations

## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/andresriancho/w3af/blob/cd22e5252243a87aaa6d0ddea47cf58dacfe00a9/w3af/plugins/attack/db/sqlmap/lib/utils/api.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```


## License: unknown
https://github.com/GianlucaZinni/api/blob/720185ac56d2f20470cac9bd4bb70378389836cc/Project/run.py

```
# Security Implementation Complete ✅

I'll now provide all security code in **English** following your project conventions.

## 1️⃣ Security Middleware Layer

````python
# filepath: c:\Users\enjoy\dev\GTS\backend\security\security_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    @staticmethod
    def setup_cors(app: FastAPI):
        """Configure CORS with secure whitelist"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "https://gabanilogistics.com",
                "https://www.gabanilogistics.com"
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
            expose_headers=["X-Total-Count"]
        )
        logger.info("✅ CORS configured securely")

    @staticmethod
    def setup_security_headers(app: FastAPI):
        """Add security headers to all responses"""
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
```

