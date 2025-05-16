# ----------------------------
# Standard & Third-Party Imports
# ----------------------------
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from celery import Celery

# ----------------------------
# Configuration & Dependencies
# ----------------------------
from config.settings import settings
from core.dependencies import get_auth_client
from src.core.api.auth_client import AuthAPIClient

# ----------------------------
# Database & Session
# ----------------------------
from backend.search.database import get_db
from src.backend.search.database.mongo_session import mongo_db  # Only if used

# ----------------------------
# Models & Schemas
# ----------------------------
from models.search import SearchIndex, SearchHistory, SearchResult
from src.backend.search.schemas.search import (
    SearchResponse,
    SearchIndexCreate,
    SearchIndexInDB,
    SearchHistoryInDB,
    SearchResultInDB,
)

# ----------------------------
# Services & Core Logic
# ----------------------------
from src.backend.search.services.search import SearchService
from src.backend.search.core.elastic_client import keyword_search
from src.backend.search.core.faiss_index import semantic_search
from src.backend.search.core.hybrid_search import hybrid_search


router = APIRouter()
search_service = SearchService()
security = HTTPBearer()
celery = Celery(
    'search',
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_RESULT_BACKEND)
)

# --- Hybrid Search Route (Primary search endpoint) ---
@router.get("/api/v1/hybrid-search", response_model=SearchResponse)
async def hybrid_search_endpoint(
    q: str = Query(..., description="Search query text"),
    filters: Optional[Dict[str, Any]] = None,
    size: int = Query(10, description="Number of results to return", ge=1, le=50),
    alpha: float = Query(0.5, description="Weight for semantic vs keyword search (0-1)", ge=0, le=1),
    index_name: str = Query("documents", description="Elasticsearch index to search"),
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Security(security),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """
    Advanced Hybrid Search combining Elasticsearch and FAISS
    
    This endpoint provides a state-of-the-art hybrid search implementation that combines:
    - Elasticsearch for keyword matching and metadata filtering
    - FAISS for semantic vector search
    - Result reranking using a weighted combination of both approaches
    
    The alpha parameter controls the balance between semantic (FAISS) and keyword (Elasticsearch) search:
    - alpha = 1.0: Pure semantic search
    - alpha = 0.0: Pure keyword search
    - alpha = 0.5: Equal weighting (default)
    """
    try:
        user_id = await auth_client.get_user_id(creds.credentials)

        # Perform hybrid search
        search_results = hybrid_search(
            query=q,
            index_name=index_name,
            filters=filters,
            size=size,
            alpha=alpha
        )
        
        # Enrich results with MongoDB data
        docs_col = mongo_db["docs"]
        hydrated_results = []
        
        for result in search_results:
            doc_id = result["id"]
            doc = docs_col.find_one({"_id": doc_id, "owner": user_id})
            
            if not doc:
                continue
                
            hydrated_results.append({
                "doc_id": doc_id,
                "title": doc.get("title", "Untitled"),
                "summary": doc.get("summary_text", ""),
                "tags": doc.get("tags", []),
                "group_id": doc.get("group_id", None),
                "score": result["score"],
                "search_type": result.get("search_type", "hybrid"),
                "rank": result.get("rank", 0)
            })

        # Log search history in Postgres
        search_history = SearchHistory(
            user_id=user_id,
            query=q,
            results_count=len(hydrated_results),
            search_type="hybrid"
        )
        db.add(search_history)
        db.commit()

        # Log top results for analysis
        for result in hydrated_results[:10]:
            search_result = SearchResult(
                search_id=search_history.id,
                document_id=result["doc_id"],
                relevance_score=result["score"]
            )
            db.add(search_result)
        db.commit()

        return SearchResponse(
            results=hydrated_results,
            total_results=len(hydrated_results),
            processing_time=0.0,  # Could be updated with actual timing info
            search_type="hybrid"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- Legacy Search Route (For backward compatibility) ---
@router.get("/api/v1/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(...),
    semantic: bool = False,
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Security(security),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """
    Legacy search endpoint (Keyword + Semantic + Mongo enrichment)
    
    For backward compatibility. New implementations should use /hybrid-search.
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