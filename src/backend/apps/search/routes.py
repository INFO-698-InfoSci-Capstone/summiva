from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from celery import Celery

from core.database.database import get_db
from core.config.settings import settings
from apps.auth.utils import get_current_user
from apps.auth.models import User
from .models import SearchIndex, SearchHistory, SearchResult
from .schemas import (
    SearchIndexCreate,
    SearchIndexInDB,
    SearchHistoryInDB,
    SearchResultInDB,
    SearchRequest,
    SearchResponse
)
from .utils import search_documents

router = APIRouter()
celery = Celery(
    'search',
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_RESULT_BACKEND)
)

@router.post("/index", response_model=SearchIndexInDB)
async def create_index(
    index: SearchIndexCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SearchIndexInDB:
    # Verify document exists and belongs to user
    document = db.query(Document)\
        .filter(Document.id == index.document_id)\
        .filter(Document.user_id == current_user.id)\
        .first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db_index = SearchIndex(
        document_id=index.document_id,
        content=index.content,
        vector=index.vector
    )
    db.add(db_index)
    db.commit()
    db.refresh(db_index)
    return db_index

@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SearchResponse:
    try:
        # Perform search
        results = search_documents(
            request.query,
            limit=request.limit,
            min_relevance=request.min_relevance
        )
        
        # Log search history
        search_history = SearchHistory(
            user_id=current_user.id,
            query=request.query,
            results_count=len(results)
        )
        db.add(search_history)
        db.commit()
        db.refresh(search_history)
        
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

@router.get("/history", response_model=List[SearchHistoryInDB])
async def get_search_history(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[SearchHistoryInDB]:
    history = db.query(SearchHistory)\
        .filter(SearchHistory.user_id == current_user.id)\
        .order_by(SearchHistory.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return history 