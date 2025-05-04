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
import sys
from pathlib import Path

# Try to ensure the config directory is in the Python path
project_root = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent.parent.parent.parent
config_dir = project_root / "config"
settings_dir = config_dir / "settings"

# Add these paths to sys.path if they're not already there
for path in [str(project_root), str(config_dir), str(settings_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Try to import settings using multiple approaches
try:
    from config.settings import settings
except ImportError:
    try:
        # Try direct import
        sys.path.insert(0, str(settings_dir))
        from settings import settings
    except ImportError:
        print(f"Warning: Could not import settings. Using default values.")
        # Create a minimal settings class
        class DefaultSettings:
            def __init__(self):
                self.CORS_ORIGINS = ["*"]
                self.RATE_LIMIT_PER_MINUTE = 100
                self.SECRET_KEY = "default_secret_key"
                self.USE_HTTPS = False
        
        settings = DefaultSettings()

from backend.core.middleware.security_middleware import InputValidationMiddleware, APISecurityMiddleware
try:
    from backend.core.security.auth_backend import JWTAuthBackend
except ImportError:
    # Create a simple auth backend if the real one can't be imported
    from starlette.authentication import AuthenticationBackend
    
    class JWTAuthBackend(AuthenticationBackend):
        async def authenticate(self, conn):
            return None

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
    try:
        app.add_middleware(InputValidationMiddleware)
        app.add_middleware(APISecurityMiddleware)
    except Exception as e:
        logger.warning(f"Failed to add security middleware: {str(e)}")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=getattr(settings, 'CORS_ORIGINS', ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted Host
    if hasattr(settings, 'ALLOWED_HOSTS'):
        try:
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=settings.ALLOWED_HOSTS,
            )
        except Exception as e:
            logger.warning(f"Failed to add TrustedHostMiddleware: {str(e)}")

    # GZIP Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Sessions
    if hasattr(settings, 'SECRET_KEY'):
        try:
            app.add_middleware(
                SessionMiddleware,
                secret_key=settings.SECRET_KEY,
                session_cookie="summiva_session",
                max_age=3600,
                same_site="lax",
                https_only=getattr(settings, 'USE_HTTPS', False),
            )
        except Exception as e:
            logger.warning(f"Failed to add SessionMiddleware: {str(e)}")

    # Authentication
    try:
        app.add_middleware(
            AuthenticationMiddleware,
            backend=JWTAuthBackend(),
        )
    except Exception as e:
        logger.warning(f"Failed to add AuthenticationMiddleware: {str(e)}")

    # Rate Limiting
    if redis_client:
        try:
            app.add_middleware(
                RateLimitMiddleware,
                redis_client=redis_client
            )
        except Exception as e:
            logger.warning(f"Failed to add RateLimitMiddleware: {str(e)}")
    
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