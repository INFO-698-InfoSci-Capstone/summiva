from typing import Optional, Dict, Any, List
from .base_client import BaseAPIClient
from core.config.settings import settings

class GroupingAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.GROUPING_SERVICE_URL)

    async def create_group(
        self,
        name: str,
        description: Optional[str] = None,
        algorithm: str = "kmeans",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new document group"""
        return await self.post(
            "/api/grouping/groups",
            json={
                "name": name,
                "description": description,
                "algorithm": algorithm,
                "parameters": parameters or {}
            }
        )

    async def group_documents(
        self,
        document_ids: List[str],
        algorithm: str = "kmeans",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Group documents using specified algorithm"""
        return await self.post(
            "/api/grouping/group",
            json={
                "document_ids": document_ids,
                "algorithm": algorithm,
                "parameters": parameters or {}
            }
        )

    async def get_group(
        self,
        group_id: str
    ) -> Dict[str, Any]:
        """Get group details"""
        return await self.get(f"/api/grouping/groups/{group_id}")

    async def get_group_members(
        self,
        group_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get documents in a group"""
        return await self.get(
            f"/api/grouping/groups/{group_id}/members",
            params={"limit": limit, "offset": offset}
        )

    async def update_group(
        self,
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update group details"""
        return await self.put(
            f"/api/grouping/groups/{group_id}",
            json={
                "name": name,
                "description": description
            }
        )

    async def delete_group(
        self,
        group_id: str
    ) -> Dict[str, Any]:
        """Delete a group"""
        return await self.delete(f"/api/grouping/groups/{group_id}")

    async def get_similar_groups(
        self,
        group_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get similar groups based on content"""
        return await self.get(
            f"/api/grouping/groups/{group_id}/similar",
            params={"limit": limit}
        ) 