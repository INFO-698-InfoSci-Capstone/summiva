"""
Password Handling Utilities
=========================
Provides consistent password hashing and verification across services.
"""
import base64
import hashlib
import os
from typing import Tuple

import bcrypt
from passlib.context import CryptContext

from backend.core.imports import setup_imports
setup_imports()

from config.settings import settings
from config.logs.logging import setup_logging

# Get logger for this module
logger = setup_logging("core.security.password")

# Password hashing settings with fallback values
try:
    SALT_ROUNDS = settings.AUTH_PASSWORD_SALT_ROUNDS
except AttributeError:
    logger.warning("AUTH_PASSWORD_SALT_ROUNDS not found in settings, using default value of 12")
    SALT_ROUNDS = 12

try:
    HASH_ALGORITHM = settings.AUTH_PASSWORD_HASH_ALGORITHM
except AttributeError:
    logger.warning("AUTH_PASSWORD_HASH_ALGORITHM not found in settings, using default value of bcrypt")
    HASH_ALGORITHM = "bcrypt"

# Create password context for hashing
pwd_context = CryptContext(
    schemes=[HASH_ALGORITHM],
    default=HASH_ALGORITHM,
    bcrypt__rounds=SALT_ROUNDS,
    deprecated="auto"
)


def get_password_hash(password: str) -> str:
    """
    Hash a password using the configured algorithm.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        bool: True if password matches hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_random_password(length: int = 12) -> str:
    """
    Generate a cryptographically secure random password.
    
    Args:
        length: Password length (default: 12)
        
    Returns:
        str: Random password
    """
    # Generate random bytes
    random_bytes = os.urandom(length)
    # Convert to base64 to get printable characters
    password = base64.urlsafe_b64encode(random_bytes)[:length].decode()
    return password


def strengthen_password(password: str, min_length: int = 8) -> Tuple[bool, str]:
    """
    Check password strength and suggest improvements.
    
    Args:
        password: Password to check
        min_length: Minimum password length
        
    Returns:
        Tuple[bool, str]: (is_strong, message)
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
        
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    issues = []
    if not has_upper:
        issues.append("uppercase letter")
    if not has_lower:
        issues.append("lowercase letter")
    if not has_digit:
        issues.append("number")
    if not has_special:
        issues.append("special character")
    
    if issues:
        return False, f"Password must include at least one {', '.join(issues)}"
    
    return True, "Password is strong"