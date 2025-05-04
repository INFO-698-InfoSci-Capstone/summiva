"""
Standard Exception Classes
=======================
Custom exception classes for standardized error handling across services.
"""
from typing import Optional, Dict, Any

from backend.core.imports import setup_imports
setup_imports()


class AppError(Exception):
    """Base exception class for all application errors"""
    
    def __init__(
        self, 
        message: str = "An unexpected error occurred", 
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)
        
    def __str__(self):
        if self.detail:
            return f"{self.message} - {self.detail}"
        return self.message


class ValidationError(AppError):
    """Raised when input data validation fails"""
    
    def __init__(
        self, 
        message: str = "Validation error", 
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=422, detail=detail)


class NotFoundError(AppError):
    """Raised when a requested resource is not found"""
    
    def __init__(
        self, 
        message: str = "Resource not found", 
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=404, detail=detail)


class DatabaseError(AppError):
    """Raised when a database operation fails"""
    
    def __init__(
        self, 
        message: str = "Database error", 
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=500, detail=detail)


class AuthenticationError(AppError):
    """Raised when authentication fails"""
    
    def __init__(
        self, 
        message: str = "Authentication failed", 
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=401, detail=detail)


class AuthorizationError(AppError):
    """Raised when authorization fails (authenticated but not permitted)"""
    
    def __init__(
        self, 
        message: str = "Not authorized", 
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=403, detail=detail)


class ServiceUnavailableError(AppError):
    """Raised when a required service is unavailable"""
    
    def __init__(
        self, 
        message: str = "Service unavailable", 
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=503, detail=detail)


class RateLimitError(AppError):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=429, detail=detail)