from typing import Optional, Dict, Any, List
from .base_client import BaseAPIClient

from config.settings.settings import settings

class TaggingAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.TAGGING_SERVICE_URL)

    async def tag_document(
        self,
        document_id: str,
        tags: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Tag a document with multiple tags"""
        return await self.post(
            "/api/tagging/tag",
            json={
                "document_id": document_id,
                "tags": tags,
                "user_id": user_id
            }
        )

    async def remove_tags(
        self,
        document_id: str,
        tags: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Remove tags from a document"""
        return await self.post(
            "/api/tagging/remove",
            json={
                "document_id": document_id,
                "tags": tags,
                "user_id": user_id
            }
        )

    async def get_document_tags(
        self,
        document_id: str
    ) -> Dict[str, Any]:
        """Get all tags for a document"""
        return await self.get(f"/api/tagging/document/{document_id}")

    async def get_tagged_documents(
        self,
        tag: str,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get all documents with a specific tag"""
        return await self.get(
            f"/api/tagging/tag/{tag}",
            params={"limit": limit, "offset": offset}
        )

    async def suggest_tags(
        self,
        document_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get suggested tags for a document"""
        return await self.get(
            f"/api/tagging/suggest/{document_id}",
            params={"limit": limit}
        ) 