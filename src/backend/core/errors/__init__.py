"""
Core Error Handling Module
========================
Provides standardized error handling utilities for all services.
"""

from backend.core.imports import setup_imports
setup_imports()

from backend.core.errors.exceptions import (
    AppError,
    DatabaseError, 
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ServiceUnavailableError
)

from backend.core.errors.handlers import (
    setup_error_handlers,
    handle_app_error,
    handle_validation_error,
    handle_auth_error,
    handle_not_found_error
)

__all__ = [
    # Exception classes
    'AppError', 'DatabaseError', 'NotFoundError', 'ValidationError',
    'AuthenticationError', 'AuthorizationError', 'ServiceUnavailableError',
    # Error handlers
    'setup_error_handlers', 'handle_app_error', 'handle_validation_error',
    'handle_auth_error', 'handle_not_found_error'
]