from typing import Optional, Dict, Any
from .base_client import BaseAPIClient

from config.settings import settings

class DocumentAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.DOCUMENT_SERVICE_URL)

    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get a document by ID"""
        return await self.get(f"/api/documents/{document_id}")

    async def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        return await self.post("/api/documents", json=document_data)

    async def update_document(self, document_id: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document"""
        return await self.put(f"/api/documents/{document_id}", json=document_data)

    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document"""
        return await self.delete(f"/api/documents/{document_id}")

    async def get_document_versions(self, document_id: str) -> Dict[str, Any]:
        """Get document versions"""
        return await self.get(f"/api/documents/{document_id}/versions")

    async def get_document_content(self, document_id: str) -> Dict[str, Any]:
        """Get document content"""
        return await self.get(f"/api/documents/{document_id}/content") 