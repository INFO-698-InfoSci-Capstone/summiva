"""
Summarization Service Client
=========================
Client for communicating with the summarization service.
"""
from typing import Dict, Any, List, Optional, Union

from backend.core.imports import setup_imports
setup_imports()

from backend.core.api_client.base import BaseAPIClient
from backend.core.api_client.factory import register_client_class


class SummarizationClient(BaseAPIClient):
    """
    Client for interacting with the summarization service
    
    This client provides high-level methods for common summarization operations.
    """
    
    async def summarize_text(
        self, 
        text: str, 
        max_length: int = 200,
        min_length: int = 50,
        model: str = "default"
    ) -> Dict[str, Any]:
        """
        Summarize a text document
        
        Args:
            text: Document text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            model: Summarization model to use
            
        Returns:
            Dict with summarization results
        """
        data = {
            "text": text,
            "max_length": max_length,
            "min_length": min_length,
            "model": model
        }
        
        result = await self.post(
            endpoint="api/summarization/summarize",
            data=data
        )
        
        return result
    
    async def get_document_summary(self, document_id: str) -> Dict[str, Any]:
        """
        Get summary for a specific document
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dict with document summary data
        """
        return await self.get(
            endpoint=f"api/summarization/documents/{document_id}/summary"
        )
    
    async def create_document(
        self, 
        title: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new document in the summarization service
        
        Args:
            title: Document title
            content: Document content
            metadata: Optional document metadata
            
        Returns:
            Dict with created document data
        """
        data = {
            "title": title,
            "content": content,
            "metadata": metadata or {}
        }
        
        return await self.post(
            endpoint="api/summarization/documents",
            data=data
        )
    
    async def get_documents(
        self,
        page: int = 1,
        size: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get paginated list of documents
        
        Args:
            page: Page number
            size: Page size
            filters: Optional filters
            
        Returns:
            Dict with paginated document list
        """
        params = {
            "page": page,
            "size": size
        }
        
        if filters:
            for key, value in filters.items():
                params[key] = value
                
        return await self.get(
            endpoint="api/summarization/documents",
            params=params
        )
    
    async def batch_summarize(
        self, 
        document_ids: List[str],
        max_length: int = 200,
        min_length: int = 50,
        model: str = "default"
    ) -> Dict[str, Any]:
        """
        Request batch summarization for multiple documents
        
        Args:
            document_ids: List of document IDs to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            model: Summarization model to use
            
        Returns:
            Dict with batch job information
        """
        data = {
            "document_ids": document_ids,
            "max_length": max_length,
            "min_length": min_length,
            "model": model
        }
        
        return await self.post(
            endpoint="api/summarization/batch",
            data=data
        )
    
    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Get status of a batch summarization job
        
        Args:
            batch_id: Batch job ID
            
        Returns:
            Dict with batch job status
        """
        return await self.get(
            endpoint=f"api/summarization/batch/{batch_id}"
        )


# Register the client class
register_client_class("summarization", SummarizationClient)