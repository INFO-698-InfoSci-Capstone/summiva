"""
JWT Authentication Utilities
==========================
Provides consistent JWT token generation and validation across services.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from backend.core.imports import setup_imports
setup_imports()

from config.settings import settings
from config.logs.logging import setup_logging

# Get logger for this module
logger = setup_logging("core.security.jwt")

# JWT token settings
ALGORITHM = settings.JWT_ALGORITHM
SECRET_KEY = settings.JWT_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class TokenPayload(BaseModel):
    """Model for JWT token payload data"""
    sub: str  # Subject (usually user ID)
    exp: int  # Expiration time
    iat: int  # Issued at time
    scope: str = "access"  # Token scope/type
    permissions: list = []  # User permissions


def create_token(
    subject: Union[str, int], 
    expires_delta: Optional[timedelta] = None,
    scope: str = "access",
    permissions: list = [],
    **extra_claims
) -> str:
    """
    Create a JWT token with standard claims.
    
    Args:
        subject: Subject identifier (usually user ID)
        expires_delta: Token expiration time delta
        scope: Token scope/type ("access" or "refresh") 
        permissions: List of user permissions
        **extra_claims: Additional claims to include in the token
        
    Returns:
        str: Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    # Calculate timestamps
    now = datetime.utcnow()
    expire = now + expires_delta
    
    # Create standard payload
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "scope": scope,
        "permissions": permissions
    }
    
    # Add any additional claims
    payload.update(extra_claims)
    
    # Create token
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extract user ID from JWT token.
    
    Args:
        token: JWT token (from OAuth2PasswordBearer dependency)
        
    Returns:
        str: User ID from token
    """
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def check_permission(token: str, required_permission: str) -> bool:
    """
    Check if a token has a specific permission.
    
    Args:
        token: JWT token string
        required_permission: Permission to check
        
    Returns:
        bool: True if token has the required permission
    """
    payload = decode_token(token)
    permissions = payload.get("permissions", [])
    return required_permission in permissions