from typing import Optional, Dict, Any, List
from .base_client import BaseAPIClient
from core.config.settings import settings

class SearchAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__(settings.SEARCH_SERVICE_URL)

    async def search_documents(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search documents with optional filters"""
        params = {
            "query": query,
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)
        return await self.get("/api/search", params=params)

    async def index_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Index a document for search"""
        return await self.post("/api/search/index", json=document_data)

    async def delete_index(self, document_id: str) -> Dict[str, Any]:
        """Delete a document from the search index"""
        return await self.delete(f"/api/search/index/{document_id}")

    async def get_search_history(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get search history for a user"""
        return await self.get(
            f"/api/search/history/{user_id}",
            params={"limit": limit, "offset": offset}
        )

    async def get_similar_documents(
        self,
        document_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get similar documents based on content"""
        return await self.get(
            f"/api/search/similar/{document_id}",
            params={"limit": limit}
        ) 