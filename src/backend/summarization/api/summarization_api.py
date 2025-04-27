from fastapi import APIRouter, Depends, HTTPException, status, Security, Query, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Database and Models
from src.backend.summarization.utils.security import fetch_user_from_auth, get_authenticated_user_id
from src.backend.auth.models import User
from src.backend.summarization.core.summarizer import summarize_text
from src.backend.summarization.models.summary import Document, Summary
from src.backend.summarization.schemas import (
    DocumentCreate, DocumentInDB, DocumentUpdate,
    SummaryInDB, SummarizationRequest, SummarizationResponse,
    DocumentFilter, SummaryFilter
)
from src.backend.summarization.utils.security import get_raw_text
from src.backend.summarization.database.mongo_session import mongo_db
from src.backend.summarization.celery_tasks.worker import run_summarization
from src.backend.core.database.database import get_db

router = APIRouter()
security = HTTPBearer()

# Create Document (PostgreSQL)
@router.post("/documents", response_model=DocumentInDB)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(fetch_user_from_auth)
) -> DocumentInDB:
    db_document = Document(
        title=document.title,
        content=document.content,
        tags=document.tags,
        user_id=current_user.id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

# Get Documents (PostgreSQL + Filtering)
@router.get("/documents", response_model=List[DocumentInDB])
def get_documents(
    filter: DocumentFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(fetch_user_from_auth)
):
    query = db.query(Document).filter(Document.user_id == current_user.id)
    if filter.tag:
        query = query.filter(Document.tags.any(filter.tag))
    if filter.title_contains:
        query = query.filter(Document.title.ilike(f"%{filter.title_contains}%"))
    return query.offset((filter.page - 1) * filter.limit).limit(filter.limit).all()

# Summarize Direct Text (Sync or Background)
@router.post("/summarize", response_model=SummarizationResponse)
async def summarize(
    request: SummarizationRequest,
    creds: HTTPAuthorizationCredentials = Security(security)
) -> SummarizationResponse:
    user_id = get_authenticated_user_id(creds)

    try:
        raw_text = request.text or get_raw_text(request.url)
        result = summarize_text(
            raw_text,
            max_length=request.max_length,
            min_length=request.min_length,
            model=request.model
        )
        return SummarizationResponse(
            summary=result["summary"],
            original_length=result["original_length"],
            summary_length=result["summary_length"],
            compression_ratio=result["compression_ratio"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Enqueue Mongo + Celery summarization task
@router.post("/enqueue", status_code=202)
def enqueue_summarization(
    req: SummarizationRequest,
    creds: HTTPAuthorizationCredentials = Security(security)
):
    user_id = get_authenticated_user_id(creds)

    try:
        raw_text = req.text or get_raw_text(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get content: {str(e)}")

    docs_col = mongo_db["docs"]
    doc_insert = docs_col.insert_one({
        "owner": user_id,
        "raw_text": raw_text,
        "summary_text": None,
        "status": "pending",
        "model": req.model.value,
        "created_at": datetime.utcnow()
    })
    doc_id = str(doc_insert.inserted_id)

    user_docs_col = mongo_db["user_docs"]
    user_docs_col.update_one(
        {"user_id": user_id},
        {"$addToSet": {"doc_ids": doc_id}},
        upsert=True
    )

    run_summarization.delay(doc_id, raw_text)
    return {"doc_id": doc_id, "status": "queued"}

# Get Summary Result (MongoDB)
@router.get("/docs/{doc_id}")
def get_doc_summary(
    doc_id: str = Path(...),
    creds: HTTPAuthorizationCredentials = Security(security)
):
    user_id = get_authenticated_user_id(creds)
    user_docs_col = mongo_db["user_docs"]
    record = user_docs_col.find_one({"user_id": user_id})
    if not record or doc_id not in record.get("doc_ids", []):
        raise HTTPException(status_code=403, detail="Document not owned by user")

    docs_col = mongo_db["docs"]
    doc_obj = docs_col.find_one(
        {"_id": ObjectId(doc_id)},
        {"raw_text": 1, "summary_text": 1, "status": 1, "model": 1}
    )
    if not doc_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "raw_text": doc_obj.get("raw_text"),
        "summary_text": doc_obj.get("summary_text"),
        "status": doc_obj.get("status", "unknown"),
        "model": doc_obj.get("model")
    }

# Summarize a stored document by ID (PostgreSQL)
@router.post("/documents/{document_id}/summarize", response_model=SummaryInDB)
def summarize_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(fetch_user_from_auth)
) -> SummaryInDB:
    document = db.query(Document)\
        .filter(Document.id == document_id, Document.user_id == current_user.id)\
        .first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        result = summarize_text(document.content)
        summary = Summary(
            document_id=document.id,
            content=result["summary"],
            length=result["summary_length"],
            model="default"
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

