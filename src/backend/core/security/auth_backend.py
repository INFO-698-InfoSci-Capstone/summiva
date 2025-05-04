"""
JWT Authentication Backend
========================
Implements Starlette's AuthenticationBackend for JWT token handling.
Used with the AuthenticationMiddleware to provide seamless JWT authentication.
"""
from typing import Optional, Tuple, Dict, Any

from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    BaseUser,
    UnauthenticatedUser
)
from starlette.requests import Request

from backend.core.security.jwt import decode_token


class JWTUser(BaseUser):
    """
    User class for JWT authenticated users.
    Implements Starlette's BaseUser interface.
    """

    def __init__(self, user_id: str, payload: Dict[str, Any]):
        self.user_id = user_id
        self.payload = payload
        self.permissions = payload.get("permissions", [])

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.user_id
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in self.permissions


class JWTAuthBackend(AuthenticationBackend):
    """
    Authentication backend for JWT token authentication.
    Implements Starlette's AuthenticationBackend interface.
    """
    
    async def authenticate(self, request: Request) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        """
        Authenticate a request using JWT token from Authorization header.
        
        Args:
            request: The incoming request to authenticate
            
        Returns:
            Optional[Tuple[AuthCredentials, BaseUser]]: Authentication credentials and user
                if authentication succeeds, otherwise None
        """
        auth_header = request.headers.get("Authorization")
        
        # If no auth header or not a Bearer token, return unauthenticated
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        # Extract token
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Decode and validate token
            payload = decode_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                return None
                
            # Get permissions from token
            permissions = payload.get("permissions", [])
            
            # Create credentials with permissions and user
            credentials = AuthCredentials(["authenticated"] + permissions)
            user = JWTUser(user_id=user_id, payload=payload)
            
            return credentials, user
            
        except Exception:
            # If token validation fails, return unauthenticated
            return None