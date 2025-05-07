from backend.search.database import get_db
from config.settings import settings
from fastapi import APIRouter, Depends, HTTPException, Security, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from src.database.mongo_session import mongo_db
from src.models.search import SearchIndex, SearchHistory, SearchResult
from src.schemas.search import (
    SearchResponse,
    SearchIndexCreate,
    SearchIndexInDB,
    SearchHistoryInDB,
    SearchResultInDB
)
from celery import Celery
from src.services.search import SearchService
from src.core.elastic_client import keyword_search
from src.core.faiss_index import semantic_search
from src.utils.security import get_authenticated_user_id
from core.dependencies import get_auth_client
from core.api.auth_client import AuthAPIClient

router = APIRouter()
search_service = SearchService()
security = HTTPBearer()
celery = Celery(
    'search',
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_RESULT_BACKEND)
)

# --- Search Route ---
@router.get("/api/v1/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(...),
    semantic: bool = False,
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Security(security),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """
    Hybrid Search (Keyword + Semantic + Mongo enrichment + History logging)
    """
    try:
        user_id = await auth_client.get_user_id(creds.credentials)

        # Keyword Search from Elastic
        keyword_results = keyword_search(q)

        # Semantic Search from FAISS
        semantic_results = semantic_search(q) if semantic else []

        # Merge results
        merged = {res["doc_id"]: res for res in keyword_results}
        for res in semantic_results:
            if res["doc_id"] in merged:
                merged[res["doc_id"]]["score"] += res["score"]
            else:
                merged[res["doc_id"]] = res

        # Enrich with MongoDB
        docs_col = mongo_db["docs"]
        hydrated = []
        for doc_id, res in merged.items():
            doc = docs_col.find_one({"_id": doc_id, "owner": user_id})
            if not doc:
                continue
            hydrated.append({
                "doc_id": doc_id,
                "title": doc.get("title", "Untitled"),
                "summary": doc.get("summary_text", ""),
                "tags": doc.get("tags", []),
                "group_id": doc.get("group_id", None),
                "score": res["score"]
            })

        # Sort results
        sorted_results = sorted(hydrated, key=lambda x: x["score"], reverse=True)

        # Log search history in Postgres
        search_history = SearchHistory(
            user_id=user_id,
            query=q,
            results_count=len(sorted_results)
        )
        db.add(search_history)
        db.commit()

        for res in sorted_results[:10]:
            search_result = SearchResult(
                search_id=search_history.id,
                document_id=res["doc_id"],
                relevance_score=res["score"]
            )
            db.add(search_result)
        db.commit()

        return SearchResponse(
            results=sorted_results[:10],
            total_results=len(sorted_results),
            processing_time=0.0  # You can update this to calculate if needed
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- Index Document Route ---
@router.post("/api/v1/index", response_model=SearchIndexInDB)
async def index_document(
    index: SearchIndexCreate,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """
    Index a document into Elastic/FAISS
    """
    try:
        await auth_client.verify_token(index.token)

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

# --- Delete Document from Index ---
@router.delete("/api/v1/index/{document_id}")
async def delete_index(
    document_id: str,
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Security(security),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """
    Delete a document from search index
    """
    try:
        await auth_client.get_user_id(creds.credentials)

        db.query(SearchIndex).filter(SearchIndex.document_id == document_id).delete()
        db.commit()

        return {"message": "Index deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- Get Search History Route ---
@router.get("/api/v1/history/{user_id}", response_model=List[SearchHistoryInDB])
async def get_search_history(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Security(security),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """
    Fetch user's search history
    """
    try:
        await auth_client.get_user_id(creds.credentials)

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

# --- Get Similar Documents Route ---
@router.get("/api/v1/similar/{document_id}", response_model=List[SearchResultInDB])
async def get_similar_documents(
    document_id: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Security(security),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """
    Fetch similar documents based on content
    """
    try:
        await auth_client.get_user_id(creds.credentials)

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