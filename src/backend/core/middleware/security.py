from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from app.core.config import settings
from app.core.security import verify_token

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

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log the request
        logger.info(
            "Request processed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "process_time": process_time,
                "status_code": response.status_code
            }
        )
        
        return response

def setup_security_middleware(app: FastAPI) -> None:
    """Configure security middleware for the application."""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    
    # Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Session
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="summiva_session",
        max_age=3600,  # 1 hour
        same_site="lax",
        https_only=settings.USE_HTTPS
    )
    
    # Authentication
    app.add_middleware(
        AuthenticationMiddleware,
        backend=JWTAuthBackend(verify_token)
    )
    
    # Rate Limiting
    app.add_middleware(
        RateLimitMiddleware,
        redis_client=settings.REDIS_CLIENT
    )
    
    # Request Logging
    app.add_middleware(RequestLoggingMiddleware)

class SecurityHeaders(BaseHTTPMiddleware):
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