from typing import Optional, Dict, Any
from .base_client import BaseAPIClient
from config.settings.settings import settings

class AuthAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.AUTH_SERVICE_URL)

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify an authentication token"""
        return await self.post("/api/auth/verify", json={"token": token})

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user information"""
        return await self.get(f"/api/auth/users/{user_id}")

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> Dict[str, Any]:
        """Check if a user has permission to perform an action on a resource"""
        return await self.post(
            "/api/auth/permissions/check",
            json={
                "user_id": user_id,
                "resource": resource,
                "action": action
            }
        )

    async def get_user_roles(self, user_id: str) -> Dict[str, Any]:
        """Get user roles"""
        return await self.get(f"/api/auth/users/{user_id}/roles") 