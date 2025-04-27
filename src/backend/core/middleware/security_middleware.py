# security_middleware.py
import re
import json
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Dict, Any, Optional, Pattern
import logging

logger = logging.getLogger(__name__)

class InputValidationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app,
        max_content_length: int = 1024 * 1024 * 10,  # 10MB default max size
        blocked_patterns: List[Pattern] = None
    ):
        super().__init__(app)
        self.max_content_length = max_content_length
        self.blocked_patterns = blocked_patterns or [
            # SQL Injection
            re.compile(r"\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b.*(FROM|INTO|WHERE)\b", re.IGNORECASE),
            # XSS
            re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
            re.compile(r"javascript:", re.IGNORECASE),
            re.compile(r"onload=", re.IGNORECASE),
            # Path traversal
            re.compile(r"\.\.\/|\.\.\\", re.IGNORECASE),
            # Command injection
            re.compile(r";\s*\w+\s*;", re.IGNORECASE),
        ]

    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("content-length", "0")
        if content_length.isdigit() and int(content_length) > self.max_content_length:
            logger.warning(f"Request content length {content_length} exceeds maximum {self.max_content_length}")
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request too large"}
            )

        # Validate request body for malicious content
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                # Skip validation for file uploads
                content_type = request.headers.get("content-type", "")
                if not content_type.startswith("multipart/form-data") and body:
                    try:
                        body_text = body.decode()
                        for pattern in self.blocked_patterns:
                            if pattern.search(body_text):
                                logger.warning(f"Blocked potentially malicious request: {pattern.pattern} matched")
                                return JSONResponse(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    content={"detail": "Invalid input detected"}
                                )
                    except UnicodeDecodeError:
                        # Binary data, skip text-based validation
                        pass
            except Exception as e:
                logger.error(f"Error during request body validation: {str(e)}")

        # Continue with the request if validation passes
        return await call_next(request)

class APISecurityMiddleware(BaseHTTPMiddleware):
    """Additional security measures for API endpoints"""
    
    async def dispatch(self, request: Request, call_next):
        # Add additional API security headers
        response = await call_next(request)
        
        # Set secure cookie policy
        if response.headers.get("set-cookie"):
            response.headers["set-cookie"] += "; SameSite=Strict; Secure; HttpOnly"
        
        # Cache control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
        return response