# core/middleware/main_middleware.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

from config.settings.settings import settings
from backend.core.middleware.security_middleware import InputValidationMiddleware, APISecurityMiddleware
from core.security.auth_backend import JWTAuthBackend  # you probably have this

logger = logging.getLogger(__name__)

# ---------------------------
# 1. Request Logging Middleware
# ---------------------------
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(
            f"{request.method} {request.url.path} completed in {process_time:.2f}s with status {response.status_code}"
        )
        
        return response

# ---------------------------
# 2. Security Headers Middleware
# ---------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self' https:;"
        )
        return response
    
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client):
        super().__init__(app)
        self.redis_client = redis_client

    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        # Get current request count
        requests = self.redis_client.get(key)
        if requests is None:
            self.redis_client.setex(key, 60, 1)  # 60 seconds expiry
        else:
            requests = int(requests)
            if requests > settings.RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"}
                )
            self.redis_client.incr(key)
        
        response = await call_next(request)
        return response

# ---------------------------
# 3. Setup all Middleware
# ---------------------------
def setup_middlewares(app: FastAPI, redis_client=None) -> None:
    # Input validation (add this first to validate incoming requests)
    app.add_middleware(InputValidationMiddleware)
    
    # API Security 
    app.add_middleware(APISecurityMiddleware)
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted Host
    if hasattr(settings, 'ALLOWED_HOSTS'):
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # GZIP Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Sessions
    if hasattr(settings, 'SECRET_KEY') and hasattr(settings, 'USE_HTTPS'):
        app.add_middleware(
            SessionMiddleware,
            secret_key=settings.SECRET_KEY,
            session_cookie="summiva_session",
            max_age=3600,
            same_site="lax",
            https_only=settings.USE_HTTPS,
        )

    # Authentication
    app.add_middleware(
        AuthenticationMiddleware,
        backend=JWTAuthBackend(),
    )

    # Rate Limiting
    if redis_client:
        app.add_middleware(
            RateLimitMiddleware,
            redis_client=redis_client
        )
    
    # Request Logging
    app.add_middleware(RequestLoggingMiddleware)

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Global Exception Handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )