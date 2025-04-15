from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from src.database.session import get_db
from src.models.search import SearchIndex, SearchHistory, SearchResult
from src.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchIndexCreate,
    SearchIndexInDB,
    SearchHistoryInDB,
    SearchResultInDB
)
from src.services.search import SearchService
from core.dependencies import get_auth_client
from core.api.auth_client import AuthAPIClient

router = APIRouter()
search_service = SearchService()

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Search documents with optional filters"""
    try:
        # Verify user token
        await auth_client.verify_token(request.token)
        
        # Perform search
        results = await search_service.search(
            query=request.query,
            filters=request.filters,
            limit=request.limit,
            offset=request.offset
        )
        
        # Log search history
        search_history = SearchHistory(
            user_id=request.user_id,
            query=request.query,
            results_count=len(results)
        )
        db.add(search_history)
        db.commit()
        
        # Log search results
        for result in results:
            search_result = SearchResult(
                search_id=search_history.id,
                document_id=result['document_id'],
                relevance_score=result['relevance_score']
            )
            db.add(search_result)
        db.commit()
        
        return SearchResponse(
            results=results,
            total_results=len(results),
            processing_time=results[0]['processing_time'] if results else 0.0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/index", response_model=SearchIndexInDB)
async def index_document(
    index: SearchIndexCreate,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Index a document for search"""
    try:
        # Verify user token
        await auth_client.verify_token(index.token)
        
        # Create search index
        db_index = SearchIndex(
            document_id=index.document_id,
            content=index.content,
            vector=index.vector
        )
        db.add(db_index)
        db.commit()
        db.refresh(db_index)
        
        return db_index
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/index/{document_id}")
async def delete_index(
    document_id: str,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Delete a document from the search index"""
    try:
        # Verify user token
        await auth_client.verify_token(request.token)
        
        # Delete index
        db.query(SearchIndex).filter(SearchIndex.document_id == document_id).delete()
        db.commit()
        
        return {"message": "Index deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history/{user_id}", response_model=List[SearchHistoryInDB])
async def get_search_history(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Get search history for a user"""
    try:
        # Verify user token
        await auth_client.verify_token(request.token)
        
        history = db.query(SearchHistory)\
            .filter(SearchHistory.user_id == user_id)\
            .order_by(SearchHistory.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/similar/{document_id}", response_model=List[SearchResultInDB])
async def get_similar_documents(
    document_id: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Get similar documents based on content"""
    try:
        # Verify user token
        await auth_client.verify_token(request.token)
        
        similar_docs = await search_service.find_similar(
            document_id=document_id,
            limit=limit
        )
        
        return similar_docs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 