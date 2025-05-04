"""
Core Security Module
==================
Provides standardized security utilities for all services.
"""

from backend.core.imports import setup_imports
setup_imports()

# JWT authentication utilities
from backend.core.security.jwt import (
    create_token,
    decode_token,
    get_current_user_id,
    check_permission,
    TokenPayload
)

# Password handling utilities
from backend.core.security.password import (
    get_password_hash,
    verify_password,
    generate_random_password,
    strengthen_password
)

__all__ = [
    # JWT utilities
    'create_token', 'decode_token', 'get_current_user_id', 'check_permission', 'TokenPayload',
    # Password utilities
    'get_password_hash', 'verify_password', 'generate_random_password', 'strengthen_password'
]